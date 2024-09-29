import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the CSV file
data = pd.read_csv('clock_data_busy.csv')

# Display the data
print(data)

# Calculate statistics
max_speed = data['ClockSpeedMHz'].max()
min_speed = data['ClockSpeedMHz'].min()
average_speed = data['ClockSpeedMHz'].mean()
std_dev_speed = data['ClockSpeedMHz'].std()

# Display the results
print(f"Max CPU Clock Speed: {max_speed:.2f} MHz")
print(f"Min CPU Clock Speed: {min_speed:.2f} MHz")
print(f"Average CPU Clock Speed: {average_speed:.2f} MHz")
print(f"Standard Deviation: {std_dev_speed:.2f} MHz")

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(data['WaitTime'], data['ClockSpeedMHz'], marker='o', linestyle='-')
plt.title('CPU Clock Speed Measurements Using SLEEP Method')
plt.xlabel('Wait Time (seconds)')
plt.ylabel('Clock Speed (MHz)')
plt.grid(True)
plt.show()
