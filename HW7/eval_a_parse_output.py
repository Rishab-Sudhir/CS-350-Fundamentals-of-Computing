import re
import csv

# Initialize data structures
data = []

# Define the regex pattern for parsing
pattern = re.compile(
    r"T(\d+) R(\d+):([\d\.]+),(\w+),(\d+),(\d+),(\d+),([\d\.]+),([\d\.]+),([\d\.]+)(?:,(\w+),(\d+))?"
)

with open('eval_a_server_output.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if not line.startswith('T'):
            continue  # Skip non-data lines
        match = pattern.match(line)
        if match:
            groups = match.groups()
            entry = {
                'thread_id': int(groups[0]),
                'req_id': int(groups[1]),
                'sent_ts': float(groups[2]),
                'img_op': groups[3],
                'overwrite': int(groups[4]),
                'client_img_id': int(groups[5]),
                'server_img_id': int(groups[6]),
                'receipt_ts': float(groups[7]),
                'start_ts': float(groups[8]),
                'compl_ts': float(groups[9]),
                'event_name': groups[10] if groups[10] else None,
                'event_count': int(groups[11]) if groups[11] else None,
            }
            # Calculate request length
            entry['req_length'] = entry['compl_ts'] - entry['start_ts']
            data.append(entry)
        else:
            print(f"Warning: Line didn't match pattern: {line}")

# Save parsed data to CSV for easy access (optional)
with open('parsed_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['img_op', 'req_length', 'event_count']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for entry in data:
        if entry['event_count'] is not None:
            writer.writerow({
                'img_op': entry['img_op'],
                'req_length': entry['req_length'],
                'event_count': entry['event_count'],
            })
