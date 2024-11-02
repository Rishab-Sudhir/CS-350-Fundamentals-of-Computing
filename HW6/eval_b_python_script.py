import re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Define operation names for easier access
operation_names = ["IMG_REGISTER", "IMG_ROT90CLKW", "IMG_BLUR", "IMG_SHARPEN", "IMG_VERTEDGES", "IMG_HORIZEDGES"]

# Regular expression to capture relevant lines in server output
line_pattern = (
    r"T(\d+)\s+"              # T<thread ID> with optional whitespace
    r"R(\d+):"                # R<req. ID>:
    r"(\d+\.\d+),"            # <sent ts>,
    r"(\w+),"                 # <img_op>,
    r"(\d),"                  # <overwrite>,
    r"(\d+),"                 # <client img_id>,
    r"(\d+),"                 # <server img_id>,
    r"(\d+\.\d+),"            # <receipt ts>,
    r"(\d+\.\d+),"            # <start ts>,
    r"(\d+\.\d+)"             # <compl. ts>
)
line_regex = re.compile(''.join(line_pattern))


def parse_server_log(filename):
    """Parse server log file and extract request lengths for each operation."""
    operations_data = {op: [] for op in operation_names}
    with open(filename, 'r') as file:
        for line in file:
            match = line_regex.search(line)
            if match:
                thread_id = int(match.group(1))
                req_id = int(match.group(2))
                sent_ts = float(match.group(3))
                operation = match.group(4)
                overwrite = int(match.group(5))
                client_img_id = int(match.group(6))
                server_img_id = int(match.group(7))
                receipt_ts = float(match.group(8))
                start_ts = float(match.group(9))
                completion_ts = float(match.group(10))
                
                request_length = completion_ts - start_ts

                # Skip IMG_RETRIEVE
                if operation != "IMG_RETRIEVE" and operation in operations_data:
                    operations_data[operation].append(request_length)

    return operations_data


def calculate_statistics(request_lengths):
    """Calculate average and 99th percentile latency."""
    if len(request_lengths) == 0:
        return float('nan'), float('nan')  # Handle empty data gracefully
    average_latency = np.mean(request_lengths)
    tail_latency_99 = np.percentile(request_lengths, 99)
    return average_latency, tail_latency_99


def plot_cdf(data, title):
    """Plot the CDF of request lengths."""
    if len(data) == 0:
        plt.title(f"{title}\nNo data available")
        plt.xlabel('Request Length (s)')
        plt.ylabel('CDF')
        return
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    plt.plot(sorted_data, cdf, marker='.', linestyle='none')
    plt.title(title)
    plt.xlabel('Request Length (s)')
    plt.ylabel('CDF')


def analyze_and_plot(run1_data, run2_data):
    fig, axs = plt.subplots(4, 3, figsize=(15, 10))
    fig.subplots_adjust(hspace=0.5, wspace=0.3)

    summary_stats = []

    for i, op in enumerate(operation_names):
        row, col = divmod(i, 3)

        # Analyze Run 1
        run1_lengths = run1_data[op]
        avg_run1, tail_run1 = calculate_statistics(run1_lengths)

        # Plot CDF for Run 1
        plt.sca(axs[row, col])
        plot_cdf(run1_lengths, f"Run 1: {op}")
        
        # Analyze Run 2
        run2_lengths = run2_data[op]
        avg_run2, tail_run2 = calculate_statistics(run2_lengths)

        # Plot CDF for Run 2
        plt.sca(axs[row + 2, col])  # Adjust row to fit both runs
        plot_cdf(run2_lengths, f"Run 2: {op}")
        
        # Collect summary statistics
        summary_stats.append({
            'operation': op,
            'avg_run1': avg_run1, 'tail_run1': tail_run1,
            'avg_run2': avg_run2, 'tail_run2': tail_run2,
            'avg_increase': avg_run2 - avg_run1,
            'tail_increase': tail_run2 - tail_run1
        })

    plt.tight_layout()
    plt.savefig("operation_cdfs.png")
    plt.show()

    return pd.DataFrame(summary_stats)

# Main analysis
run1_data = parse_server_log("./eval_b_outputs/server_output_run1.log")
run2_data = parse_server_log("./eval_b_outputs/server_output_run2.log")

summary_df = analyze_and_plot(run1_data, run2_data)
print(summary_df)

# Save the summary statistics to a CSV for reference
summary_df.to_csv("latency_summary.csv", index=False)
