import numpy as np
import matplotlib.pyplot as plt
import re

def parse_request_lengths(filename):
    """Parse request lengths from output file, excluding IMG_RETRIEVE operations."""
    request_lengths = []
    with open(filename, 'r') as file:
        for line in file:
            # Match the pattern for a request line
            match = re.match(r"T\d+ R\d+:(\d+\.\d+),(\w+),(\d+),(\d+),(\d+),(\d+\.\d+),(\d+\.\d+),(\d+\.\d+)", line)
            if match:
                img_op = match.group(2)
                if img_op == "IMG_RETRIEVE":
                    continue  # Exclude IMG_RETRIEVE

                receipt_timestamp = float(match.group(6))
                completion_timestamp = float(match.group(8))
                request_length = completion_timestamp - receipt_timestamp
                request_lengths.append(request_length)

    return np.array(request_lengths)

def calculate_statistics(request_lengths):
    """Calculate average and 99% tail latency for request lengths."""
    avg_latency = np.mean(request_lengths)
    tail_latency_99 = np.percentile(request_lengths, 99)
    return avg_latency, tail_latency_99

def plot_cdf(request_lengths, title, ax):
    """Plot CDF for request lengths."""
    sorted_lengths = np.sort(request_lengths)
    cdf = np.arange(1, len(sorted_lengths) + 1) / len(sorted_lengths)
    ax.plot(sorted_lengths, cdf, marker='.', linestyle='none')
    ax.set_xlabel("Request Length (s)")
    ax.set_ylabel("CDF")
    ax.set_title(title)

    # Calculate statistics
    avg_latency, tail_latency_99 = calculate_statistics(request_lengths)
    ax.axvline(avg_latency, color='r', linestyle='--', label=f'Average: {avg_latency:.6f} s')
    ax.axvline(tail_latency_99, color='g', linestyle='--', label=f'99% Tail: {tail_latency_99:.6f} s')
    ax.legend()

# Define file paths for the three outputs
files = {
    '-O0': './eval_d_outputs/O0_server_output_run2.log',
    '-O1': './eval_d_outputs/O1_server_output_run2.log',
    '-O2': './eval_d_outputs/O2_server_output_run2.log'
}

# Create subplots for the three optimization levels
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("CDF of Request Lengths for Different Optimization Levels")

# Process each file and create a CDF plot
for idx, (opt_level, file_path) in enumerate(files.items()):
    request_lengths = parse_request_lengths(file_path)
    plot_cdf(request_lengths, f"Optimization Level {opt_level}", axes[idx])

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("request_lengths_cdf.png")
plt.show()
