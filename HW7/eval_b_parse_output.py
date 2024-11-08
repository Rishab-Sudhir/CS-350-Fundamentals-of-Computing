import re
import json

def parse_server_output(filename):
    # Initialize a dictionary to store data per operation
    data_per_op = {}
    pattern = re.compile(
        r"T\d+ R\d+:[\d\.]+,(\w+),\d+,\d+,\d+,[\d\.]+,[\d\.]+,[\d\.]+,(\w+),(\d+)"
    )
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('T'):
                continue
            match = pattern.search(line)
            if match:
                img_op = match.group(1)
                event_name = match.group(2)
                event_count = int(match.group(3))
                if event_name == 'LLCMISS' and img_op != 'IMG_REGISTER' and img_op != 'IMG_RETRIEVE':
                    if img_op not in data_per_op:
                        data_per_op[img_op] = []
                    data_per_op[img_op].append(event_count)
            else:
                print(f"Warning: Line didn't match pattern: {line}")
    return data_per_op

# Parse RUN1 and RUN2 outputs
llc_miss_run1 = parse_server_output('eval_b_server_output_run1.txt')
llc_miss_run2 = parse_server_output('eval_b_server_output_run2.txt')

# Save data to JSON files for plotting
with open('llc_miss_run1.json', 'w') as f:
    json.dump(llc_miss_run1, f)

with open('llc_miss_run2.json', 'w') as f:
    json.dump(llc_miss_run2, f)
