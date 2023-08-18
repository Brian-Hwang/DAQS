import argparse
import subprocess
import time
import os
import re
import datetime

# Default values
default_values = {
    "ip": "20.0.1.4",
    "base_dir": os.path.dirname(os.path.realpath(__file__)),
    "duration": "60",
    "window_size": "2m",
    "message_size": "1500",
    "test_times": 5,
    "loop_on": "parallel",
    "start_value": 1,
    "end_value": 5,
    "delay_minutes": 0
}

# Set up command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-i", "--ip", default=default_values["ip"], help=f"set the IP address (default: {default_values['ip']})")
parser.add_argument("-d", "--base_dir", default=default_values["base_dir"],
                    help=f"set the base directory for output files (default: directory of this script)")
parser.add_argument("-u", "--duration", default=default_values["duration"],
                    help=f"set the duration (default: {default_values['duration']})")
parser.add_argument("-w", "--window_size", default=default_values["window_size"],
                    help=f"set the window size (default: {default_values['window_size']})")
parser.add_argument("-m", "--message_size", default=default_values["message_size"],
                    help=f"set the message size (default: {default_values['message_size']})")
parser.add_argument("-t", "--test_times", default=default_values["test_times"],
                    type=int, help=f"set the test times (default: {default_values['test_times']})")
parser.add_argument("-l", "--loop_on", default=default_values["loop_on"],
                    help=f"set what to loop on (duration, window_size, message_size, parallel, nothing, - default: {default_values['loop_on']})")
parser.add_argument("-s", "--start_value", default=default_values["start_value"], type=int,
                    help=f"set the start value for loop (default: {default_values['start_value']})")
parser.add_argument("-e", "--end_value", default=default_values["end_value"], type=int,
                    help=f"set the end value for loop (default: {default_values['end_value']})")
parser.add_argument("-n", "--delay_minutes", default=default_values["delay_minutes"], type=int,
                    help=f"delay the start of the script by N minutes (default: {default_values['delay_minutes']})")
parser.add_argument("-c", "--cron_time", default=None,
                    help="set the time to start the script in HH:MM format")

args = parser.parse_args()


# join the base directory and the filename to get the full path
output_file = os.path.join(args.base_dir, "results.txt")

# check if file exists then delete it
if os.path.isfile(output_file):
    try:
        os.remove(output_file)
    except Exception as e:
        print(f"Error while deleting file {output_file}. Error message: {e}")
else:
    print(f"The file '{output_file}' does not exist.")


if args.cron_time:
    cron_hour, cron_minute = map(int, args.cron_time.split(':'))
    now = datetime.datetime.now()
    start_time = datetime.datetime(
        now.year, now.month, now.day, cron_hour, cron_minute)
    if start_time <= now:
        # Run the next day if the time has already passed
        start_time += datetime.timedelta(days=1)
    delay_seconds = (start_time - now).total_seconds()
    print(f"Delaying the start of the script by {delay_seconds} seconds...")
    time.sleep(delay_seconds)


# Delay the start of the script if the --delay_minutes option was used
if args.delay_minutes > 0:
    print(
        f"Delaying the start of the script by {args.delay_minutes} minute(s)...")
    time.sleep(args.delay_minutes * 60)

# Outer loop for TEST_TIMES times execution
for j in range(1, args.test_times + 1):
    # Inner loop
    for i in range(args.start_value, args.end_value + 1):
        print(f"Running iperf with loop on {args.loop_on} and value {i}")

        # now = datetime.datetime.now()
        # next_run_time = now + datetime.timedelta(minutes=(1 - now.minute % 1))
        # delay_seconds = (next_run_time - now).seconds
        # if delay_seconds > 0:
        #     print(
        #         f"Delaying the start of the loop by {delay_seconds} second(s) to synchronize with the 5-minute interval...")
        #     time.sleep(delay_seconds)

        # Depending on the value of LOOP_ON, we'll change a different parameter
        command = f"iperf -c {args.ip} -t {args.duration} -w {args.window_size} -P 1 -l {args.message_size} -i 10"

        if args.loop_on == "duration":
            command = f"iperf -c {args.ip} -t {i} -w {args.window_size} -P 1 -l {args.message_size} -i 10"
        elif args.loop_on == "window_size":
            command = f"iperf -c {args.ip} -t {args.duration} -w {i}m -P 1 -l {args.message_size} -i 10"
        elif args.loop_on == "message_size":
            command = f"iperf -c {args.ip} -t {args.duration} -w {args.window_size} -P 1 -l {i}K -i 10"
        elif args.loop_on == "nothing":
            command = f"iperf -c {args.ip} -t {args.duration} -w {args.window_size} -P 1 -l {args.message_size} -i 30"
        else:
            command = f"iperf -c {args.ip} -t {args.duration} -w {args.window_size} -P {i} -i 30"

        # Run command and capture the output
        output = subprocess.run(command, shell=True,
                                stdout=subprocess.PIPE).stdout.decode()

        # Append output to the file
        with open(output_file, 'a') as f:
            f.write(f"Results for {args.loop_on}={i}, iteration {j}:\n")
            f.write(output)
            f.write("\n" + "-"*50 + "\n")
