import csv
import re
import argparse


def extract_bandwidth(txt_file_path, csv_file_path):
    # Initialize list to store data
    data_list = []

    # Read the .txt file and parse data
    with open(txt_file_path, 'r') as file:
        for line in file:
            # Regular expression to extract interval and sum bandwidth
            match = re.match(
                r'\[SUM\]\s+(\d+\.\d+-\d+\.\d+ sec)\s+(\d+(?:\.\d+)? [GT]Bytes)\s+(\d+(?:\.\d+)?)', line)
            if match:
                interval, transfer, bandwidth = match.groups()

                # Remove units from transfer, if needed
                transfer_value, transfer_unit = re.match(
                    r'(\d+(?:\.\d+)?) ([GT]Bytes)', transfer).groups()
                if transfer_unit == 'GBytes':
                    transfer_value = float(transfer_value) * 1000
                transfer = str(transfer_value)

                data_list.append([interval, transfer, bandwidth])

    # Write data to the CSV file
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Interval', 'Transfer (MBytes)',
                        'Bandwidth (bits/sec)'])  # Write header
        writer.writerows(data_list)  # Write data


def main():
    parser = argparse.ArgumentParser(
        description="Convert bandwidth text file to CSV")
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Path to the text file containing the bandwidth data')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Path to the CSV file where the data will be saved')
    args = parser.parse_args()

    extract_bandwidth(args.input, args.output)


if __name__ == "__main__":
    main()
