#!/bin/bash

# Default values
IP="20.0.1.4"
BASE_DIR="$(dirname "$0")"
DURATION="60"
WINDOW_SIZE="2m"
Message_SIZE="1500"
TEST_TIMES=5
LOOP_ON="parallel"
START_VALUE=1
END_VALUE=5

# Help message
usage() {
    echo "Usage: $0 [-i IP] [-d BASE_DIR] [-u DURATION] [-w WINDOW_SIZE] [-m Message_SIZE] [-t TEST_TIMES] [-l LOOP_ON] [-s START_VALUE] [-e END_VALUE]"
    echo
    echo "  -i  set the IP address (default: 20.0.1.4)"
    echo "  -d  set the base directory for output files (default: directory of this script)"
    echo "  -u  set the duration (default: 60)"
    echo "  -w  set the window size (default: 2m)"
    echo "  -m  set the message size (default: 1500)"
    echo "  -t  set the test times (default: 5)"
    echo "  -l  set what to loop on (duration, window_size, message_size, parallel - default: parallel)"
    echo "  -s  set the start value for loop (default: 1)"
    echo "  -e  set the end value for loop (default: 5)"
    exit 1
}

# Parse command-line options
while getopts ":hi:d:u:w:m:t:l:s:e:" opt; do
  case ${opt} in
    h) usage ;;
    i) IP="$OPTARG" ;;
    d) BASE_DIR="$OPTARG" ;;
    u) DURATION="$OPTARG" ;;
    w) WINDOW_SIZE="$OPTARG" ;;
    m) Message_SIZE="$OPTARG" ;;
    t) TEST_TIMES="$OPTARG" ;;
    l) LOOP_ON="$OPTARG" ;;
    s) START_VALUE="$OPTARG" ;;
    e) END_VALUE="$OPTARG" ;;
    \?) echo "Invalid option -$OPTARG" >&2; usage ;;
  esac
done

# Outer loop for TEST_TIMES times execution
for (( j=1; j<=TEST_TIMES; j++ ))
do
  # Inner loop 
  for (( i=START_VALUE; i<=END_VALUE; i++ ))
  do
    echo "Running iperf with loop on $LOOP_ON and value $i"
    
    # Depending on the value of LOOP_ON, we'll change a different parameter
    case $LOOP_ON in
        duration)
            output=$(iperf -c $IP -t $i -w $WINDOW_SIZE -P 1 -l $Message_SIZE)
            ;;
        window_size)
            output=$(iperf -c $IP -t $DURATION -w "${i}m" -P 1 -l $Message_SIZE)
            ;;
        message_size)
            output=$(iperf -c $IP -t $DURATION -w $WINDOW_SIZE -P 1 -l "${i}K")
            ;;
        *)
            output=$(iperf -c $IP -t $DURATION -w $WINDOW_SIZE -P $i -l $Message_SIZE)
            ;;
    esac
    
    # Extract the bandwidth value, assuming it's the last field in the output
    bandwidth=$(echo "$output" | tail -n 3 | awk '{print $(NF-1)}' | tail -n 1)
    
    # Convert bandwidth (assumed to be in Mbits/sec) to a number
    bandwidth_num=$(echo $bandwidth | sed 's/[A-Za-z]*//g')

    # Output file
    OUTPUT_FILE="${BASE_DIR}/results.txt"

    # Write bandwidth to file
    echo "Bandwidth for $LOOP_ON=$i, iteration $j: $bandwidth_num Gbits/sec" >> $OUTPUT_FILE
  done
done
