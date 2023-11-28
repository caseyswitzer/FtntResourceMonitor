# Ftnt (Fortinet) Resource Monitoring Script

## Overview
The Ftnt Resource Monitoring Script is designed for use with FortiGate firewalls. It fetches, visualizes, and reports on system resources from the "/monitor/system/resource" API endpoint, handling data such as CPU usage, memory utilization, and disk activity, and presenting this information in an HTML report.

This script was tested on FortiOS version 7.0 and 7.2.

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
Navigate to the script's directory to run the script. Here are some usage examples:

- **Run with Default Settings**:
  If a `config.py` file exists with correct entries, simply run the following.  This will use the default resource selection and API details from `config.py`.
  ```bash
  python ftntrm.py
  ```

- **Specify Resources and Disable SSL Verification (use with caution)**:
  ```bash
  python ftntrm.py -r cpu mem disk --no_ssl_verify
  ```

- **Specify API Details and Use a Certificate**:
  ```bash
  python ftntrm.py --base_url https://api.example.com:<port> --access_token YOUR_TOKEN --cert_file path/to/certfile.pem
  ```

## Using Certificates
You need a certificate to validate the SSL certificate of the server you're connecting to. This typically means:

- **CA Certificate**: If the server uses a certificate signed by a Certificate Authority (CA), the `--cert_file` should contain the CA's certificate or the root certificate that can validate the chain of trust.  The certificate can also be installed the Windows certificate store.
- **Server's Public Certificate**: If the server uses a self-signed certificate, the `--cert_file` should contain that specific self-signed certificate to establish trust.

### Types of Certificates Supported
- The script supports PEM (.pem) and DER (.cer/.crt) certificates.

### Behavior with `--cert_file` and `--no_ssl_verify`
- **Specifying `--cert_file`**: When you use the `--cert_file` option with the path to a certificate file, the script will use this certificate for SSL/TLS verification.
- **Not Specifying `--cert_file`**:
  - **On Windows**: The script will default to using the Windows certificate store.
  - **On Unix/Linux/macOS**: The script will use the default set of CA certificates provided by the `certifi` package.
- **Specifying `no_ssl_verify`**:
  - Disabling SSL verification (`--no_ssl_verify`) can expose you to security risks like man-in-the-middle attacks, especially on untrusted networks. Use this option only in secure, isolated environments.

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
