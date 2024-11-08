import numpy as np
import matplotlib.pyplot as plt
import json

# Load data
with open('eval_c_l1miss_blur.json', 'r') as f:
    blur_l1miss = json.load(f)

with open('eval_c_l1miss_sharpen.json', 'r') as f:
    sharpen_l1miss = json.load(f)

# Convert to numpy arrays
blur_l1miss = np.array(blur_l1miss)
sharpen_l1miss = np.array(sharpen_l1miss)

# Define bins with increments of 10,000
bins = np.arange(0, max(blur_l1miss.max(), sharpen_l1miss.max()) + 10000, 10000)

# Calculate normalized frequencies separately for each dataset
blur_counts, _ = np.histogram(blur_l1miss, bins=bins)
sharpen_counts, _ = np.histogram(sharpen_l1miss, bins=bins)

# Normalize each by its total count to get separate normalized frequencies
blur_freq = blur_counts / blur_counts.sum()
sharpen_freq = sharpen_counts / sharpen_counts.sum()

# Plot
plt.figure(figsize=(14, 7))

# Plot bars for each distribution with some offset for visibility
plt.bar(bins[:-1] - 5000, blur_freq, width=8000, color='blue', alpha=0.6, label='IMG_BLUR')
plt.bar(bins[:-1] + 5000, sharpen_freq, width=8000, color='orange', alpha=0.6, label='IMG_SHARPEN')

# Add fewer x-axis labels to avoid overcrowding
plt.xticks(bins[::10], rotation=45)  # Show every 10th bin label

# Add summary statistics (mean) as vertical lines with annotations
blur_mean = blur_l1miss.mean()
sharpen_mean = sharpen_l1miss.mean()
plt.axvline(blur_mean, color='blue', linestyle='--', linewidth=1.5, label=f'Blur Mean: {int(blur_mean)}')
plt.axvline(sharpen_mean, color='orange', linestyle='--', linewidth=1.5, label=f'Sharpen Mean: {int(sharpen_mean)}')

# Set axis labels and title
plt.xlabel('L1 Cache Misses (in increments of 10,000)')
plt.ylabel('Normalized Frequency (0 to 1)')
plt.title('Normalized Distribution of L1 Cache Misses for IMG_BLUR and IMG_SHARPEN')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)

# Limit y-axis between 0 and 1 for normalized data
plt.ylim(0, 1)

# Save and show the plot
plt.tight_layout()
plt.savefig('l1miss_distribution_improved.png')
plt.show()
