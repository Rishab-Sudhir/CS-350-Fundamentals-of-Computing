# Example data (replace with your actual data)
run_numbers = list(range(1, 11))

# runtime data
part1_runtimes = [5.96, 8.03, 10.29, 12.57, 14.59, 16.82, 18.89, 21.22, 23.33, 25.86]
part2_runtimes = [5.03, 5.99, 6.9, 7.85, 8.77, 9.77, 10.77, 11.63, 12.77, 13.6]
part3_runtimes = [4.52, 5.34, 6.09, 6.93, 7.76, 8.64, 9.45, 10.19, 10.99, 11.98]

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))

# Plot Part 1
plt.plot(run_numbers, part1_runtimes, marker='o', label='Part 1 (w=1)')

# Plot Part 2
plt.plot(run_numbers, part2_runtimes, marker='s', label='Part 2 (w=10)')

# Plot Part 3
plt.plot(run_numbers, part3_runtimes, marker='^', label='Part 3 (w=10, New Mid)')

# Labels and Title
plt.title('Total Server Runtime vs. Number of Mid Section Repetitions')
plt.xlabel('Number of Mid Section Repetitions')
plt.ylabel('Total Server Runtime (seconds)')
plt.legend()
plt.grid(True)
plt.xticks(run_numbers)
plt.show()
