import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

# Read parsed data
data = pd.read_csv('eval_a_parsed_data.csv')

# List of image operations
img_ops = data['img_op'].unique()

# Set up the plotting grid
num_ops = len(img_ops)
cols = 3
rows = (num_ops + cols - 1) // cols  # Ceiling division
fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
axes = axes.flatten()

# Dictionary to store regression coefficients
regression_results = {}

for idx, img_op in enumerate(img_ops):
    ax = axes[idx]
    op_data = data[data['img_op'] == img_op]
    sns.scatterplot(
        x='event_count', y='req_length', data=op_data, ax=ax, label=img_op, alpha=0.5
    )
    sns.regplot(
        x='event_count', y='req_length', data=op_data, ax=ax,
        scatter=False, color='red', label='Best Fit'
    )
    ax.set_title(img_op)
    ax.set_xlabel('Instruction Count')
    ax.set_ylabel('Request Length (s)')
    ax.legend()

    # Perform linear regression
    X = op_data[['event_count']]
    y = op_data['req_length']
    model = LinearRegression()
    model.fit(X, y)
    coef = model.coef_[0]
    intercept = model.intercept_
    regression_results[img_op] = {'slope': coef, 'intercept': intercept}

    # Display regression equation on the plot
    ax.text(
        0.05, 0.95,
        f'y = {coef:.2e}x + {intercept:.2e}',
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment='top'
    )

# Remove any empty subplots
for idx in range(len(img_ops), len(axes)):
    fig.delaxes(axes[idx])

plt.tight_layout()
plt.savefig('instruction_vs_req_length.png')
plt.show()

# Print regression results
for img_op, params in regression_results.items():
    print(f"{img_op}: y = {params['slope']:.2e}x + {params['intercept']:.2e}")
