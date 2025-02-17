# extract_SR

## Overview

extract_SR is a Python script that uses API call to automatically downlaod specimen requirements (SRs) from list of CPs provided in the input file. All the SRs are downloaded in a output folder defined in the configuration file.

### Usage Instructions
1. Install Dependencies
```python
pip3 install pandas
pip3 install requests
```

2. Configure config.ini
Example structure:

```python
[API_CALL]
os_user = os_login_name
os_password = os_login_password
os_domain = openspecimen
os_url = https://demo.openspecimen.org

[SETTINGS]
file_path = /path/to/input_file.csv
output_folder = /path/to/output_folder
```

4. Run the Script
```python
python3 extract_SR.py
```

5. Check Output
- The script created a output folder and saves all the SR files in it.
- A log file (extract_SR.log.log) is created to track execution.
