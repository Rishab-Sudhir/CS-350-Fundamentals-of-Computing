import numpy as np
import matplotlib.pyplot as plt
import json

# Load data
with open('eval_b_llc_miss_run1.json', 'r') as f:
    llc_miss_run1 = json.load(f)

with open('eval_b_llc_miss_run2.json', 'r') as f:
    llc_miss_run2 = json.load(f)

# Get the list of image operations
img_ops = sorted(set(llc_miss_run1.keys()).union(set(llc_miss_run2.keys())))

# Determine grid size (e.g., 2 rows x 3 columns)
num_ops = len(img_ops)
cols = 3
rows = (num_ops + cols - 1) // cols  # Ceiling division

# Set up the plotting grid
fig, axes = plt.subplots(rows, cols, figsize=(18, 6 * rows))
axes = axes.flatten()

# Iterate over each image operation
for idx, img_op in enumerate(img_ops):
    ax = axes[idx]

    # Get data for RUN1 and RUN2
    data_run1 = llc_miss_run1.get(img_op, [])
    data_run2 = llc_miss_run2.get(img_op, [])

    # Convert to numpy arrays
    data_run1 = np.array(data_run1)
    data_run2 = np.array(data_run2)

    if len(data_run1) == 0 or len(data_run2) == 0:
        print(f"No data for operation {img_op} in one of the runs.")
        ax.axis('off')  # Hide the subplot if no data
        continue

    # Compute statistics
    mean_run1 = np.mean(data_run1)
    mean_run2 = np.mean(data_run2)

    min_run1 = np.min(data_run1)
    min_run2 = np.min(data_run2)

    max_run1 = np.max(data_run1)
    max_run2 = np.max(data_run2)

    print(f"{img_op} - RUN1: MIN = {min_run1}, MAX = {max_run1}, MEAN = {mean_run1}")
    print(f"{img_op} - RUN2: MIN = {min_run2}, MAX = {max_run2}, MEAN = {mean_run2}")

    # Sort data for CDF
    sorted_run1 = np.sort(data_run1)
    sorted_run2 = np.sort(data_run2)

    # Compute CDF values
    cdf_run1 = np.arange(1, len(sorted_run1) + 1) / len(sorted_run1)
    cdf_run2 = np.arange(1, len(sorted_run2) + 1) / len(sorted_run2)

    # Plotting
    ax.plot(sorted_run1, cdf_run1, label='RUN1')
    ax.plot(sorted_run2, cdf_run2, label='RUN2')

    # Add vertical lines for mean values
    ax.axvline(mean_run1, color='blue', linestyle='--', label=f'RUN1 Mean: {mean_run1:.2f}')
    ax.axvline(mean_run2, color='orange', linestyle='--', label=f'RUN2 Mean: {mean_run2:.2f}')

    # Set labels and title
    ax.set_xlabel('LLC Cache Misses')
    ax.set_ylabel('CDF')
    ax.set_title(f'LLC Misses CDF - {img_op}')
    ax.legend()
    ax.grid(True)

# Remove any empty subplots
for idx in range(len(img_ops), len(axes)):
    fig.delaxes(axes[idx])

#plt.tight_layout()
plt.savefig('llc_miss_cdf_grid.png')
plt.show()
