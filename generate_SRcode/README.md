# generate_SRcode

# Overview

generate_SRcode is a Python script that automatically generates Specimen Requirement (SR) codes for a given CSV file of specimen requirements. The generated codes help in uniquely identifying specimens within different events of a collection protocol.

# Logic for SR Code Generation

# Initialize Mapping with the First Event:
- Read the first event and sequentially generate SR codes for each specimen.
- The code is stored in a key-value format, where the key is derived as Key = (Lineage + Type + Initial Quantity + Collection Container)

# Process Subsequent Events and Update Mapping:
- If a new SR is found in a later event, it updated mapping with new SR.
- If an existing SR is repeated multiple times in later events, a new sequence is generated using the formula:
Existing Sequence + (n) [where n is the repetition count in the new event]

# Configuration File (config.ini)
A configuration file (config.ini), which must include:
- Path to the input CSV file.
- Path to the output CSV file.

# Future Enhancements
- Support for multiple Collection Protocols in a single input file.
- Auto-population of parent SR codes based on specimen hierarchy.

# Usage Instructions
1. Install Dependencies
pip install pandas

2. Configure config.ini
Example structure:

[SETTINGS]
file_path = path/to/input.csv
output_file = path/to/output.csv

4. Run the Script
python3 generate_SRcode.py

4. Check Output
- The script generates an output CSV with an auto-populated "Code" column for specimen requirements.
- A log file (logfile.log) is created to track execution.
