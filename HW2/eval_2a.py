import re

def parse_server_log(log_file_path):

    """
    Parses the server log and extracts completion timestamps
    and queue sizes.

    returns a list of tuples: (completion_timestamp, queue_size)
    """

    pattern_r = re.compile(r'^R\d+:(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+)$')
    pattern_q = re.compile(r'^Q:\[(.*?)\]$')

    data = []
    current_completion_time = None

    with open(log_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Check for R line
            match_r = pattern_r.match(line)

            if match_r:
                # Extract completion time (5th value)
                completion_time = float(match_r.group(5))
                current_completion_time = completion_time
                continue # move to the next line to find Q

            """
            Logic Here for match_q:

            Non-Empty Queue (Q:[R1,R2,R3]):
            queue_contents = match_q.group(1)
            queue_contents = "R1,R2,R3"
            queue_contents.strip() == ''
            "R1,R2,R3".strip() → "R1,R2,R3"
            "R1,R2,R3" == '' → False
            Else Block:
            queue_size = queue_contents.count('R') → 3 (R1, R2, R3)
            """
            match_q = pattern_q.match(line)
            if match_q and current_completion_time is not None:
                # Extract queue size by counting requests in Q
                queue_contents = match_q.group(1)
                if (queue_contents.strip() == ""):
                    queue_size = 0
                else:
                    # Count number of 'R' entries
                    queue_size = queue_contents.count("R")
                # Append the tuple
                data.append((current_completion_time, queue_size))
                current_completion_time = None # Reset for next R
                continue
    return data

def compute_time_weighted_average(data):
    """
    Computes the time-weighted average queue size.
    'data' is a list of tuples: (completion_timestamp, queue_size)
    """

    if not data:
        return 0.0
    
    total_time_weighted_queue = 0.0
    total_time = 0.0

    for i in range (len(data)):
        current_time, current_queue = data[i]
        if i < len(data) - 1:
            # more than 2 entries left
            next_time = data[i+1][0]
            duration = next_time - current_time
        else:
            # for the last 2 entries assume the duration is the same as previous
            if len(data) >= 2:
                duration = data[i][0] - data[i-1][0]
            else:
                duration = 0 # last data point

        if duration < 0:
            print(f"Warning: Negative duration between {current_time} and {next_time}. Skipping")
            continue
        total_time_weighted_queue += duration * current_queue
        total_time += duration

    if total_time == 0:
        return 0.0
    
    average = total_time_weighted_queue/total_time

    return average

def main():
    log_file = './2a_server_log.txt'
    data = parse_server_log(log_file)
    average_queue_size = compute_time_weighted_average(data)
    print(f"Time-Weighted Average Queue Size: {average_queue_size:.4f}")

if __name__ == "__main__":
    main()
