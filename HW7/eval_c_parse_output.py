import re
import json

def parse_server_output(filename):
    blur_l1miss = []
    sharpen_l1miss = []
    pattern = re.compile(
        r"T\d+ R\d+:[\d\.]+,(IMG_BLUR|IMG_SHARPEN),\d+,\d+,\d+,[\d\.]+,[\d\.]+,[\d\.]+,(\w+),(\d+)"
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
                if event_name == 'L1MISS':
                    if img_op == 'IMG_BLUR':
                        blur_l1miss.append(event_count)
                    elif img_op == 'IMG_SHARPEN':
                        sharpen_l1miss.append(event_count)
            else:
                print(f"Warning: Line didn't match pattern: {line}")
    return blur_l1miss, sharpen_l1miss

# Parse the server output
blur_l1miss, sharpen_l1miss = parse_server_output('eval_c_server_output.txt')

# Save data to files for plotting
with open('eval_c_l1miss_blur.json', 'w') as f:
    json.dump(blur_l1miss, f)

with open('eval_c_l1miss_sharpen.json', 'w') as f:
    json.dump(sharpen_l1miss, f)
