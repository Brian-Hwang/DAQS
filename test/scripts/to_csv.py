import csv
import re

# Path to the text file
txt_file_path = 'results.txt'

# Initialize dictionary to store data
data_dict = {}

# Initialize a set to record unique parallel numbers
parallel_set = set()

# Read the .txt file and parse data
with open(txt_file_path, 'r') as file:
    for line in file:
        # Regular expression to extract parallel, iteration, and bandwidth
        match = re.match(
            r'Bandwidth for parallel=(\d+), iteration (\d+): (\d+\.\d+) Gbits/sec', line)
        if match:
            parallel = int(match.group(1))
            iteration = int(match.group(2))
            # Convert Gbits/sec to Mbits/sec
            bandwidth = float(match.group(3)) * 1000

            # Add bandwidth to data dictionary
            if iteration not in data_dict:
                data_dict[iteration] = {}
            data_dict[iteration][parallel] = bandwidth

            # Record the parallel number
            parallel_set.add(parallel)

# Path to the .csv file
csv_file_path = 'results.csv'

# Sort the parallel numbers
sorted_parallels = sorted(list(parallel_set))

# Write data to the .csv file
with open(csv_file_path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Iteration'] + ['P{}'.format(p)
                    for p in sorted_parallels])  # Header row
    for iteration, bandwidths in sorted(data_dict.items()):
        writer.writerow([iteration] + [bandwidths.get(p, '')
                        for p in sorted_parallels])
