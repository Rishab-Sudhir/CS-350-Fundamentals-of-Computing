import re
import pandas as pd
import matplotlib.pyplot as plt

def read_server_logs(log_file_path):
    """
    Reads and parses the server log file to extract request information and queue sizes.

    Args:
        log_file_path (str): Path to the server log file.

    Returns:
        pd.DataFrame: DataFrame containing request details and corresponding queue sizes.
    """
    # Define regex patterns for request and queue lines
    request_pattern = re.compile(r'^R(\d+):(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+)$')
    queue_pattern = re.compile(r'^Q:\[([R\d,]*)\]$')

    data = []

    with open(log_file_path, 'r') as file:
        for line in file:
            line = line.strip()

            # Match request lines
            req_match = request_pattern.match(line)
            if req_match:
                req_id = int(req_match.group(1))
                sent_ts = float(req_match.group(2))
                req_len = float(req_match.group(3))
                recv_ts = float(req_match.group(4))
                start_ts = float(req_match.group(5))
                comp_ts = float(req_match.group(6))
                data.append({
                    'req_id': req_id,
                    'sent_ts': sent_ts,
                    'req_len': req_len,
                    'recv_ts': recv_ts,
                    'start_ts': start_ts,
                    'comp_ts': comp_ts,
                    'queue_size': 0  # Placeholder for queue size
                })
                continue  # Proceed to next line

            # Match queue lines
            q_match = queue_pattern.match(line)
            if q_match and data:
                queue_contents = q_match.group(1)
                if queue_contents.strip() == "":
                    queue_size = 0
                else:
                    # Count number of 'R' entries indicating requests in queue
                    queue_size = queue_contents.count('R')
                # Assign queue size to the most recent request
                data[-1]['queue_size'] = queue_size

    return pd.DataFrame(data)

def compute_weighted_average_queue_size(df):
    """
    Computes the time-weighted average queue size based on request timestamps.

    Args:
        df (pd.DataFrame): DataFrame containing request details and queue sizes.

    Returns:
        float: Time-weighted average queue size.
    """
    if df.empty:
        return 0.0

    total_time_weighted_queue = 0.0
    total_time = 0.0

    for i in range(len(df)):
        current_time = df['start_ts'].iloc[i]
        current_queue = df['queue_size'].iloc[i]

        if i < len(df) - 1:
            next_time = df['start_ts'].iloc[i + 1]
            duration = next_time - current_time
        else:
            if len(df) >= 2:
                duration = current_time - df['start_ts'].iloc[i - 1]
            else:
                duration = 0  # No duration for single entry

        if duration < 0:
            print(f"Warning: Negative duration between {current_time} and {next_time}. Skipping.")
            continue

        total_time_weighted_queue += duration * current_queue
        total_time += duration

    if total_time == 0:
        return 0.0

    average = total_time_weighted_queue / total_time
    return average

def calculate_server_utilization(df):
    """
    Calculates the server utilization based on busy time and total experiment duration.

    Args:
        df (pd.DataFrame): DataFrame containing request details.

    Returns:
        float: Server utilization ratio.
    """
    if df.empty:
        return 0.0

    total_busy_time = (df['comp_ts'] - df['start_ts']).sum()
    experiment_start = df['recv_ts'].min()
    experiment_end = df['comp_ts'].max()
    experiment_duration = experiment_end - experiment_start

    if experiment_duration <= 0:
        return 0.0

    utilization = total_busy_time / experiment_duration
    return utilization

def calculate_average_response_time(df):
    """
    Calculates the average response time for all requests.

    Args:
        df (pd.DataFrame): DataFrame containing request details.

    Returns:
        float: Average response time in seconds.
    """
    if df.empty:
        return 0.0

    df['response_time'] = df['comp_ts'] - df['recv_ts']
    average_response_time = df['response_time'].mean()
    return average_response_time

def main():
    # Initialize lists to store metrics for each experiment
    utilization_values = []
    average_response_times = []
    average_queue_sizes = []

    # Run experiments for a parameter sweep from 1 to 15
    for a in range(1, 16):
        log_file = f'./logs/server_a{a}.txt' 
        print(f"Processing log file: {log_file}")

        # Parse the server log
        df = read_server_logs(log_file)

        # Compute metrics
        avg_queue_size = compute_weighted_average_queue_size(df)
        utilization = calculate_server_utilization(df)
        avg_response_time = calculate_average_response_time(df)

        # Store metrics for plotting
        utilization_values.append(utilization)
        average_queue_sizes.append(avg_queue_size)
        average_response_times.append(avg_response_time)

        # Output results for the current experiment
        print(f"Results for a={a}:")
        print(f"  Average Queue Size: {avg_queue_size:.4f}")
        print(f"  Server Utilization: {utilization:.4f}")
        print(f"  Average Response Time: {avg_response_time:.4f} seconds\n")

    # Create a DataFrame for plotting
    results_df = pd.DataFrame({
        'Utilization': utilization_values,
        'Average Response Time': average_response_times,
        'Average Queue Size': average_queue_sizes
    })

    # Save results to a CSV file for later analysis
    results_df.to_csv('./results/experiment_results.csv', index=False)
    print("Experiment results saved to './results/experiment_results.csv'.")

    fig, ax1 = plt.subplots(figsize=(12, 8))

    color = 'tab:blue'
    ax1.set_xlabel('Server Utilization')
    ax1.set_ylabel('Average Response Time', color=color)
    ax1.plot(results_df['Utilization'], results_df['Average Response Time'], label='Average Response Time', marker='o', linestyle='-', color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis

    color = 'tab:red'
    ax2.set_ylabel('Average Queue Size', color=color)
    ax2.plot(results_df['Utilization'], results_df['Average Queue Size'], label='Average Queue Size', marker='x', linestyle='--', color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.title('Average Response Time and Queue Size vs Server Utilization')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
