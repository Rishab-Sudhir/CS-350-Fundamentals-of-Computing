import re
import matplotlib.pyplot as plt
import numpy as np

# Define the policies and the corresponding log files
policies = {
    'FIFO': 'EVAL_B_logs/FIFO/server_40.log',
    'SJN': 'EVAL_B_logs/SJN/server_40.log'
}

# Regular expression to parse the log lines
log_pattern = re.compile(
    r'T(\d+) R(\d+):([\d\.]+),([\d\.]+),([\d\.]+),([\d\.]+),([\d\.]+)'
)

# Dictionary to store response times for each policy
response_times = {}

for policy, log_file in policies.items():
    response_times[policy] = []

    with open(log_file, 'r') as f:
        for line in f:
            match = log_pattern.match(line.strip())
            if match:
                # Extract the timestamps
                req_timestamp = float(match.group(3))
                completion_time = float(match.group(7))

                # Calculate response time
                resp_time = completion_time - req_timestamp

                # Append to the list
                response_times[policy].append(resp_time)

    print(f"Policy: {policy}, Number of Requests: {len(response_times[policy])}")

# Dictionary to store statistics
stats = {}

for policy in policies.keys():
    times = response_times[policy]
    times.sort()  # Sort the response times

    # Calculate average response time
    avg_response_time = np.mean(times)

    # Calculate 99th percentile response time
    percentile_99 = np.percentile(times, 99)

    # Store in stats dictionary
    stats[policy] = {
        'average': avg_response_time,
        'percentile_99': percentile_99,
        'sorted_times': times  # Store sorted times for CDF plot
    }

    print(f"Policy: {policy}")
    print(f"  Average Response Time: {avg_response_time:.4f} seconds")
    print(f"  99th Percentile Response Time: {percentile_99:.4f} seconds")

# Function to plot the CDF
def plot_cdf(times, avg_time, percentile_99, policy_name, x_limits, y_limits):
    # Calculate the CDF values
    sorted_times = np.sort(times)
    cdf = np.arange(1, len(sorted_times)+1) / len(sorted_times)

    # Plot the CDF
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_times, cdf, label=f'CDF of Response Times ({policy_name})')

    # Add vertical lines for average and 99th percentile
    plt.axvline(x=avg_time, color='r', linestyle='--', label='Average Response Time')
    plt.axvline(x=percentile_99, color='g', linestyle='--', label='99th Percentile Response Time')

    # Set the x and y limits to make plots comparable
    plt.xlim(x_limits)
    plt.ylim(y_limits)

    # Labels and Title
    plt.xlabel('Response Time (seconds)')
    plt.ylabel('Cumulative Probability')
    plt.title(f'CDF of Response Times - {policy_name} Policy')
    plt.legend()
    plt.grid(True)

    # Save the plot
    plt.savefig(f'cdf_response_times_{policy_name.lower()}.png')
    plt.show()

# Determine common x and y limits based on combined data for comparability
all_times = response_times['FIFO'] + response_times['SJN']
x_min = 0
x_max = max(all_times) * 1.05  # Slightly greater than max to give some space
y_min = 0
y_max = 1

x_limits = (x_min, x_max)
y_limits = (y_min, y_max)

# Plot for each policy
for policy in policies.keys():
    times = stats[policy]['sorted_times']
    avg_time = stats[policy]['average']
    percentile_99 = stats[policy]['percentile_99']

    plot_cdf(times, avg_time, percentile_99, policy, x_limits, y_limits)
