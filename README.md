# Ftnt (Fortinet) Resource Monitoring Script

## Overview
The Ftnt Resource Monitoring Script is designed for use with FortiGate firewalls. It fetches, visualizes, and reports on system resources from the "/monitor/system/resource" API endpoint, handling data such as CPU usage, memory utilization, and disk activity, and presenting this information in an HTML report.

This script was tested on FortiOS version 7.2.6.

## Features
- **Resource Flexibility**: Customize the set of resources (like CPU, memory, disk) to monitor.
- **HTML Reporting**: Automatically generate detailed reports with embedded graphs.
- **SSL Verification Control**: Option to enable or disable SSL certificate verification.

## Getting Started

### Prerequisites
- Python 3.x
- Pip (Python package installer)

### Installation
1. **Clone the Repository**
   ```bash
   git clone https://github.com/caseyswitzer/FtntResourceMonitor.git
   cd FtntResourceMonitor
   ```

2. **Install Required Libraries**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration File (optional)
Create a `config.py` file in the `src` directory with the Base URL and Access Token:
```python
# config.py
BASE_URL = "https://Your_FortiGate_IP_or_Hostname:<port>" 
ACCESS_TOKEN = "Your_Access_Token"
```
- Navigate to `src`, create `config.py`, and replace the placeholders with your actual information.

### Usage
Navigate to the script's directory, then:
- **Specify resources**:
  ```bash
  python main.py -r cpu mem disk
  ```
- **Use default resources**:
  ```bash
  python main.py
  ```
- **Specify API details**:
  ```bash
  python main.py --base_url https://api.example.com:<port> --access_token YOUR_TOKEN
  ```
- **Disable SSL certificate verification** (caution advised):
  ```bash
  python main.py --no_ssl_verify
  ```

## Report Generation
Reports are saved in the `reports` directory:
```
[parent_directory]/reports/report_YYYYMMDD_HHMMSS.html
```
Ensure script has write permissions to this directory. It will attempt to create the directory if it doesn't exist.

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
