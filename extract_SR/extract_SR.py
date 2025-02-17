import pandas as pd
import configparser
import logging
import traceback
import sys
import requests
from urllib.parse import urljoin
import os


def start_logging(path):
    logging.basicConfig(
        filename = path,  # Log file path
        level = logging.DEBUG,  # Log level set to DEBUG for capturing detailed logs
        format = '%(asctime)s - %(levelname)s - %(message)s'
    )    


def load_config(config_file="config.ini"):
    """Load configuration from the config.ini file."""
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def load_csv(file_path):
    """Load the CSV file and return a DataFrame."""

    logging.info(f"Loading csv file: {file_path}")

    data = pd.read_csv(file_path, dtype=str, low_memory=True, quotechar='"', escapechar='\\').fillna('')

    logging.info(f"CSV loaded successfully with {len(data)} rows and {len(data.columns)} columns.")
    
    return data


def get_api_token(login_name, password, domain_name, os_url):
    """Get the API token for the session."""

    token_url = urljoin(os_url, "rest/ng/sessions")

    print(token_url)
    
    login_payload = {
        "loginName": login_name,
        "password": password,
        "domainName": domain_name
    }

    token_headers = {"Content-Type": "application/json"}
    token_response = requests.post(token_url, json=login_payload, headers=token_headers)

    if token_response.status_code == 200:
        token = token_response.json().get('token')
        logging.info(f"Token obtained successfully!")
    else:
        logging.error(f"Failed to get token: {token_response.text}")
        exit(1)
    
    return token


def extact_cp_spmn_req(os_url, token, cp_id, short_title):
    """Fetch Export ID for Specimen Requirementd export Job."""

    spmn_req_url =  urljoin(os_url, "rest/ng/export-jobs")

    spmn_req_payload = {
        "objectType": "sr",
        "params": {
            "cpId": cp_id
        }
    }

    spmn_req_headers = {
        "Content-Type": "application/json",
        "X-OS-API-TOKEN": token
    }

    spmn_req_response = requests.post(spmn_req_url, headers=spmn_req_headers, json=spmn_req_payload)

    if spmn_req_response.status_code == 200:
        export_job_id = "rest/ng/export-jobs/" + str(spmn_req_response.json().get('id')) + "/output"
        logging.info(f"Export Job ID extracted successfully for {short_titile}.")
    else:
        logging.error(f"Failed to get specimen requirements: {spmn_req_response.text}")
        sys.exit(1)

    return export_job_id


def save_sr(os_url, token, export_job_id ,output_folder, short_titile):
    """Download Specimen requirement of a Collection Protocol."""

    export_job_url =  urljoin(os_url, export_job_id)

    export_headers = {
    "X-OS-API-TOKEN": token
    }

    exprot_response = requests.get(export_job_url, headers=export_headers, stream=True)

    file_name = short_titile + ".zip"

    output_path = os.path.join(output_folder, file_name)

    if exprot_response.status_code == 200:
        with open(output_path, "wb") as file:
            for chunk in exprot_response.iter_content(chunk_size=8192):
                file.write(chunk)
        logging.info(f"Download specimen requirement successfully for {short_titile}")
    else:
        logging.error(f"Failed to download. Status code: {exprot_response.status_code}, Response: {exprot_response.text}")


if __name__ == "__main__":

    try:
        config = load_config()

        # Credentials Details
        login_name = config["API_CALL"]["os_user"]
        password = config["API_CALL"]["os_password"]
        domain_name = config["API_CALL"]["os_domain"]
        os_url = config["API_CALL"]["os_url"]

        # File and folder Details
        file_path = config["SETTINGS"]["file_path"]
        output_folder = config["SETTINGS"]["output_folder"]
        log_file = "extract_SR.log"

        start_logging(log_file)

        # Load input file
        cp_details = load_csv(file_path)

        # Extract API token for the session
        api_token = get_api_token(login_name, password, domain_name, os_url)

        # Create the folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Loop through one CP at a time
        for index, cp in cp_details.iterrows():
            cp_id = cp["identifier"]
            short_titile = cp["short_title"]

            # Trigger the API to run export job and fetch its ID
            download_id = extact_cp_spmn_req(os_url, api_token, cp_id, short_titile)

            # Save the file in the output folder
            save_sr(os_url, api_token, download_id ,output_folder, short_titile)

    except Exception as err:
        logging.error(f"Encountered an error: {err}")
        logging.error(traceback.format_exc())  # Capture full traceback
        sys.exit(1)