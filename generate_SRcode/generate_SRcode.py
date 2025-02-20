import pandas as pd
import configparser
import logging
import traceback
import sys
import os
import zipfile


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

    # Open the zip file and read the 'output.csv' directly using pandas
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        with zip_ref.open('output.csv') as file:
            data = pd.read_csv(file, dtype=str, low_memory=True, quotechar='"', escapechar='\\').fillna('')

    logging.info(f"CSV loaded successfully with {len(data)} rows and {len(data.columns)} columns.")
    
    return data


def req_code_map(spmn_req):
    """Generate unique requirement codes for specimens."""

    events = spmn_req["Event Label"].unique()
    
    code_map = {}
    code = 1 
        
    # Process the first event separately
    first_event = spmn_req[spmn_req["Event Label"] == events[0]]

    for index, req in first_event.iterrows():
        key = (
            str(req["Lineage"]) + "_" + 
            str(req["Specimen Class"]) + "_" + 
            str(req["Specimen Type"]) + "_" + 
            #str(req["Initial Quantity"]) + "_" + 
            str(req["Collection Container"])
        )

        code_map.setdefault(key, []).append(code)
        code += 1

    # Process subsequent events and update code_map
    for event in events[1:]:
        counter = {key: 0 for key in code_map.keys()}  # Reset counter for tracking assignments

        update_code_map = {}

        for index, req in spmn_req[spmn_req["Event Label"] == event].iterrows():

            key = (
                str(req["Lineage"]) + "_" + 
                str(req["Specimen Class"]) + "_" + 
                str(req["Specimen Type"]) + "_" + 
                #str(req["Initial Quantity"]) + "_" + 
                str(req["Collection Container"])
            )
 
            if key in code_map:
                pos = counter[key]  # Use current counter position
                if pos < len(code_map[key]):
                    counter[key] += 1  # Increment counter if existing codes are available
                else:
                    code_map[key].append(code)
                    code += 1
            else:
                update_code_map.setdefault(key, []).append(code)
                code += 1

        code_map.update(update_code_map)

    return code_map


def assign_sr_code(spmn_req, code_map):
    """Populate the requirement code for matching specimens."""

    previous_event = None

    for index, req in spmn_req.iterrows():

        current_event = str(req["Event Label"])

        if current_event != previous_event:
            counter = {key: 0 for key in code_map.keys()}

        key = (
            str(req["Lineage"]) + "_" + 
            str(req["Specimen Class"]) + "_" + 
            str(req["Specimen Type"]) + "_" + 
            #str(req["Initial Quantity"]) + "_" + 
            str(req["Collection Container"])
        )
        
        if key in code_map:  # Ensure key exists in the code_mapping

            pos = counter[key]  # Use current counter position

            if pos < len(code_map[key]):  # Ensure pos is within the list length
                spmn_req.at[index, "Code"] = code_map[key][pos]
                counter[key] += 1  # Increment counter only after successful assignment
            else:
                logging.error(f"Warning: No more codes available for key {key}, skipping index {index}")
        else:
            logging.error(f"Warning: Key {key} not found in code_map, skipping index {index}")

        previous_event = current_event

    return spmn_req


def asign_parent_code(spmn_req):
    """Populte requirment code of the parent specimen to the child row."""

    # Create a mapping of Unique UID to Code

    uid_to_code = spmn_req.set_index('Unique ID')['Code']

    # Populate Parent Code using Parent UID
    spmn_req['Parent Code'] = spmn_req['Parent UID'].map(uid_to_code)

    return spmn_req


def save_to_csv(req_with_code):
    """Save the DataFrame to an csv."""
    req_with_code.to_csv(output_file, index=False)
    logging.info(f"Data saved successfully to: {output_file}")


def merge_csv(output_folder):
    """Merge all csv output in one."""

    # Get a list of all CSV files in the folder
    csv_files = [file for file in os.listdir(output_folder) if file.endswith('.csv')]

    # List to store the dataframes
    all_data = []

    # Loop through each file and read it into a dataframe
    for file in csv_files:
        file_path = os.path.join(output_folder, file)
        data = pd.read_csv(file_path)
        all_data.append(data)

    # Concatenate all dataframes into one
    merged_data = pd.concat(all_data, ignore_index=True)

    # Save the merged dataframe to a new CSV file
    merged_file_path = os.path.join(output_folder, "0-All_CPs_SR.csv")

    merged_data.to_csv(merged_file_path, index=False)

    logging.info(f"All Specimen Requirement files merged into {merged_file_path} successfully!")

if __name__ == "__main__":

    try:
        config = load_config()

        folder_path = config["SETTINGS"]["folder_path"]
        output_folder = config["SETTINGS"]["output_folder"]
        log_file = "generate_SRcode.log"

        start_logging(log_file)

        # Get a list of all CSV files in the folder
        files = [file for file in os.listdir(folder_path) if file.endswith('.zip')]

        # Make a output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Process one file at a time
        for file in files:
            file_path = os.path.join(folder_path, file)
            output_file = os.path.join(output_folder, file.replace(".zip",".csv"))

            # Load Specimen Requirement
            spmn_req = load_csv(file_path)

            # Check if the CP has data or not before generate mapping
            if len(spmn_req) == 0:
                logging.error("There is no data.")
                continue

            # Generate mapping
            mapping = req_code_map(spmn_req)

            # Assign code to respective specimens
            spmn_req = assign_sr_code(spmn_req, mapping)

            # Assign code to parent specimen
            spmn_req = asign_parent_code(spmn_req)

            # Save the updated Specimen Requirement
            save_to_csv(spmn_req)

        # Merge all Specimen Requirement in single file
        merge_csv(output_folder)   
        
    except Exception as err:
        logging.error(f"Encountered an error: {err}")
        logging.error(traceback.format_exc())  # Capture full traceback
        sys.exit(1)
