import re
import csv

def parse_bandwidth_data(data):
    category_data = {}
    target_gbps_pattern = r'(\d+(?:\.\d+)?)\sGbps\s+limit:'
    current_speed_pattern = r'Bandwidth\s+for\s+parallel=\d+,\s+iteration\s+(\d+):\s+(\d+\.\d+)\sGbits/sec'
    section_pattern = r'Result\s+for\s+([\w.-]+):(.*?)(?=Result\s+for\s+|$)'
    data_parts = data.strip().split('========================')

    max_iterations = -1

    for part in data_parts:
        target_gbps_matches = re.findall(target_gbps_pattern, part)
        if not target_gbps_matches:
            target_gbps = '-1'
        else:
            target_gbps = target_gbps_matches[0]

        sections = re.findall(section_pattern, part, re.DOTALL)
        for section_name, section_content in sections:
            current_speeds = re.findall(current_speed_pattern, section_content)
            if section_name not in category_data:
                category_data[section_name] = {}
            for iteration, speed in current_speeds:
                if target_gbps not in category_data[section_name]:
                    category_data[section_name][target_gbps] = {}
                category_data[section_name][target_gbps][int(iteration)] = speed
                if max_iterations < int(iteration):
                    max_iterations = int(iteration)

    return category_data, max_iterations

with open('result_raw.txt', 'r') as file:
    data = file.read()

category_data, max_iterations = parse_bandwidth_data(data)

with open('results.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    header = ['Target Gbps limit', 'Category'] + [f'Speed {i}' for i in range(1, max_iterations + 1)]
    csv_writer.writerow(header)
    for category_name, category_dict in category_data.items():
        for target_gbps, speeds in category_dict.items():
            row_data = [target_gbps, category_name]
            for i in range(1, max_iterations + 1):
                row_data.append(speeds.get(i, None))
            csv_writer.writerow(row_data)