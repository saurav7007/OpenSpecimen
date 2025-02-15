# generate_SRcode

The script auto-generated the specimen requirement code for the input csv file of specimen requirement.

The reqirement code is generated based on below logic:
1. Read the first event and sequencially generate requirement code for every specimen within the event. The code is saved in a key and pair format where key = (Lineage + Type + Initial Qty + Collection Container) 
2. Read remaining event and update the above mapping if:
  i) The new specimen is found based on key.
  ii) The existinng specimen sequence is updated.

The config file need below inputs:
1. The path of input csv file
2. The path of out csv file.
