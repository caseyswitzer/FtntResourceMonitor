import argparse
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
import base64
import certifi
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException, SSLError
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
try:
    from config import BASE_URL as CONFIG_BASE_URL, ACCESS_TOKEN as CONFIG_ACCESS_TOKEN
except ModuleNotFoundError:
    CONFIG_BASE_URL = None
    CONFIG_ACCESS_TOKEN = None

# Command line arguments setup
def setup_argparse() -> argparse.Namespace:
    """
    Set up and configure the argument parser for command-line inputs.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description=(
            'Generate a report for specified resources.\n\n'
            'This script allows configuration of BASE_URL and ACCESS_TOKEN either through '
            'command line arguments or via a config.py file. If provided, command line arguments '
            'will override the settings in config.py.\n\n'
            'Usage Examples:\n'
            '1. Run with Default Settings (using config.py):\n   ftntrm.py\n'
            '2. Specify Resources and Disable SSL Verification:\n   ftntrm.py -r cpu mem disk --no_ssl_verify\n'
            '3. Specify API Details and Use a Certificate:\n   ftntrm.py --base_url https://api.example.com:<port> --access_token YOUR_TOKEN --cert_file path/to/certfile.pem\n\n'
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Define the choice resources for monitoring
    resources_choices = [
        'cpu', 'mem', 'disk', 'session', 'session6', 'setuprate',
        'setuprate6', 'disk_lograte', 'faz_lograte', 'forticloud_lograte',
        'gtp_tunnel', 'gtp_tunnel_setup_rate'
    ]
    
    # Define default resources excluding 'gtp_tunnel' and 'gtp_tunnel_setup_rate'
    default_resources = [
        'cpu', 'mem', 'disk', 'session', 'session6', 'setuprate',
        'setuprate6', 'disk_lograte', 'faz_lograte', 'forticloud_lograte'
    ]

    # Adding arguments to the parser for command-line configurability
    parser.add_argument(
        '-r',
        choices=resources_choices,
        nargs='*',
        default=default_resources, 
        metavar='RESOURCE',
        help=('You can specify one or more resources separated by spaces.\n'
              f'Available choices: {", ".join(resources_choices)}')
    )
    
    # Optional BASE_URL argument
    parser.add_argument(
        '--base_url',
        type=str,
        help='Base URL for the API.'
    )

    # Optional ACCESS_TOKEN argument
    parser.add_argument(
        '--access_token',
        type=str,
        help='Access token for API authentication.'
    )

    # Optional argument to disable SSL certificate verification
    parser.add_argument(
        '--no_ssl_verify',
        action='store_true',
        help='Disable SSL certificate verification and suppress SSL warnings.'
    )

    # Optional argument for SSL certificate file
    parser.add_argument(
        '--cert_file',
        type=str,
        help='Path to the SSL certificate file (.crt, .cer, or .pem format).'
    )  

    # Optional argument for VDOM scope
    parser.add_argument(
        '--scope',
        type=str,
        default='global',  
        choices=['vdom', 'global'],
        help='Scope of resource [vdom|global]. Applicable if the FortiGate is in VDOM mode.'
    )

    # Parse and return the arguments
    return parser.parse_args()

# API request function
def get_resource_data(resource: str, base_url: str, access_token: str, ssl_verify: bool = True, cert_file: str = None, scope: str = 'global') -> dict:
    """
    Retrieve data for a specified resource from the API.

    Args:
        resource (str): The name of the resource to fetch data for.
        base_url (str): The base URL of the API.
        access_token (str): Access token for API authentication.
        ssl_verify (bool): Flag to determine SSL certificate verification.
        cert_file (str, optional): Path to an SSL certificate file for verification.
        scope (str): Scope of the resource ('vdom' or 'global'), applicable in VDOM mode.

    Returns:
        dict: The data retrieved from the API for the specified resource, or None if an error occurs.
    """
    # Disable SSL warnings if SSL verification is not required
    if not ssl_verify:
        urllib3.disable_warnings(InsecureRequestWarning)

    # Constructing the API request URL
    base_url = base_url.rstrip('/')
    url = f"{base_url}/api/v2/monitor/system/resource/usage?access_token={access_token}&resource={resource}&scope={scope}"
    
    try:
        # Making the API request and parsing the response
        ssl_cert_path = cert_file if cert_file else (certifi.where() if ssl_verify else False)
        response = requests.get(url, verify=ssl_cert_path)
        #print("API Response:", response.text) # Debug
        response.raise_for_status()
        return response.json()
    except (SSLError, HTTPError, ConnectionError, Timeout, RequestException) as err:
        print(f"Error occurred: {err}")
        return None

# Function to plot data for any resource
def plot_resource_data(resource_name: str, timeframe: str, timeframe_data: dict) -> None:
    """
    Extract and plot data for a given resource and timeframe.

    Args:
        resource_name (str): Name of the resource to plot.
        timeframe (str): Timeframe for which data is plotted.
        timeframe_data (dict): Data to be plotted.
    """
    try:
        # Convert timestamps to datetime objects and extract resource values
        timestamps = [datetime.fromtimestamp(ts[0] / 1000) for ts in timeframe_data['values']]
        resource_values = [ts[1] for ts in timeframe_data['values']]

        # Check and reverse the order of data points if in reverse chronological order
        if timestamps and timestamps[0] > timestamps[-1]:
            timestamps.reverse()
            resource_values.reverse()

        # Plot configuration and styling
        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, resource_values, marker='o')
        plt.title(f"{resource_name} - {timeframe} timeframe")
        plt.xlabel("Time")
        plt.ylabel(f"{resource_name}")

        # Setting dynamic Y-axis range based on resource values
        max_value = max(resource_values) if resource_values else 0
        buffer = max_value * 0.1 if max_value > 100 else 10 
        if resource_name in ['CPU', 'Memory']:
            ymax = min(max_value + buffer, 100)  
        else:
            # For non-percentage resources, allow the y-axis to exceed 100 if necessary
            ymax = max_value + buffer  
        plt.ylim(0, ymax)

        # X-axis formatting with labels for every other tick
        plt.xlim(timestamps[0], timestamps[-1]) if timestamps else None
        plt.xticks(ticks=[timestamps[i] for i in range(len(timestamps))])
        ax = plt.gca()
        for index, label in enumerate(ax.get_xticklabels()):
            if index % 2 != 0:
                label.set_visible(False)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.gcf().autofmt_xdate()

        # Adding annotations for date and resource statistics
        current_date = timestamps[0].strftime('%Y-%m-%d') if timestamps else ''
        plt.annotate(f'Date: {current_date}', xy=(0.01, 0.95), xycoords='axes fraction', fontsize=9)

        # Combine stats into a single string
        stats = {'Min': timeframe_data.get('min', 0), 'Max': timeframe_data.get('max', 0), 'Avg': timeframe_data.get('average', 0)}
        stats_string = ", ".join([f"{key}: {val}" for key, val in stats.items()])
        plt.annotate(stats_string, xy=(0.95, 0.95), xycoords='axes fraction', horizontalalignment='right', fontsize=9)

    except (KeyError, TypeError) as e:
        print(f"Error processing data for {resource_name}: {e}")
        return

# Function to save plots as images
def save_plot_image(resource_name: str, timeframe: str, timeframe_data: dict) -> str:
    """
    Plot the resource data and save it as a base64 encoded image.

    This function first calls plot_resource_data to create a plot, then saves the plot
    as a PNG image in a BytesIO buffer. This buffer is then encoded into a base64 string.

    Args:
        resource_name (str): The name of the resource to be plotted.
        timeframe (str): The timeframe over which data is plotted.
        timeframe_data (dict): The data to be plotted.

    Returns:
        str: A base64 encoded string of the plotted image.
    """
    plot_resource_data(resource_name, timeframe, timeframe_data)
    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    return "data:image/png;base64," + base64.b64encode(img.getvalue()).decode('utf-8')

# Function to generate HTML report
def generate_html_report(data: dict) -> None:
    """
    Generate an HTML report from the provided data.

    This function uses Jinja2 templating to render an HTML report that includes the
    plots of resource data. The report is saved in a 'reports' directory.

    Args:
        data (dict): The data to be included in the report. This should be a dictionary
                     where keys are resource names and values are lists of data points.

    Returns:
        None
    """
    script_dir = Path(__file__).resolve().parent
    parent_dir = script_dir.parent
    templates_dir = parent_dir / 'templates'
    reports_dir = parent_dir / 'reports'

    # Create the reports directory if it does not exist
    if not reports_dir.exists():
        reports_dir.mkdir(parents=True)

    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('report_template.html')

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"report_{timestamp}.html"
    report_file_path = reports_dir / report_filename

    # Write the rendered HTML content to a file
    with open(report_file_path, 'w') as file:
        html_content = template.render({'data': data})
        file.write(html_content)
    
    print(f"Report saved as {report_file_path}")

# Main script execution
if __name__ == "__main__":
    try:
        # Parsing command-line arguments
        args = setup_argparse()

        # Configuration setup for API interaction
        ssl_verify = not args.no_ssl_verify 
        BASE_URL = args.base_url if args.base_url else CONFIG_BASE_URL
        ACCESS_TOKEN = args.access_token if args.access_token else CONFIG_ACCESS_TOKEN

        # Check if BASE_URL and ACCESS_TOKEN have been set either via CLI or config.py
        if not BASE_URL or not ACCESS_TOKEN:
            print("Error: BASE_URL and ACCESS_TOKEN must be set either via the CLI or in a config.py file.")
            sys.exit(1)
     
        # Data fetching and report generation logic
        resources_to_report = args.r
        resources = {}

        for resource in resources_to_report:
            response_data = get_resource_data(resource, BASE_URL, ACCESS_TOKEN, ssl_verify=ssl_verify, cert_file=args.cert_file, scope=args.scope)
            if response_data and 'results' in response_data and resource in response_data['results']:
                resources[resource.upper()] = response_data['results'][resource][0]['historical']

        report_data = {}
        for resource_name, resource_data in resources.items():
            report_data[resource_name] = []
            for timeframe, data in resource_data.items():
                image_path = save_plot_image(resource_name, timeframe, data)
                report_data[resource_name].append({'timeframe': timeframe, 'image': image_path})

        generate_html_report(report_data)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
