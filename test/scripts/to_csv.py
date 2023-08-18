import csv
import re
import argparse


def convert_txt_to_csv(txt_file_path, csv_file_path):
    # Initialize dictionary to store data
    data_dict = {}

    # Initialize a set to record unique parallel numbers
    parallel_set = set()

    # Read the .txt file and parse data
    with open(txt_file_path, 'r') as file:
        for line in file:
            # Regular expression to extract parallel, iteration, bandwidth, and unit
            match = re.match(
                r'Bandwidth for \w+=(\d+), iteration (\d+): (\d+\.\d+) (Gbits/sec|Mbits/sec)', line)
            if match:
                parallel = int(match.group(1))
                iteration = int(match.group(2))
                bandwidth = float(match.group(3))
                unit = match.group(4)

                # Convert Mbits/sec to Gbits/sec if needed
                if unit == "Mbits/sec":
                    bandwidth /= 1000

                # Add bandwidth to data dictionary
                if iteration not in data_dict:
                    data_dict[iteration] = {}
                data_dict[iteration][parallel] = bandwidth

                # Record the parallel number
                parallel_set.add(parallel)

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


def main():
    parser = argparse.ArgumentParser(
        description='Convert a text file to a CSV file.')
    parser.add_argument(
        '-i', '--input', help='Input text file path', required=True)
    parser.add_argument(
        '-o', '--output', help='Output CSV file path', required=True)

    args = parser.parse_args()

    convert_txt_to_csv(args.input, args.output)


if __name__ == "__main__":
    main()
