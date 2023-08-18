#!/bin/bash

# Maximum value of n (you can change this to the desired value)
max_n=7

# Initial sleep before starting the loop
echo "Initial sleep for 60 seconds..."
sleep 60

# Loop from 1 to max_n
for n in $(seq 1 $max_n); do
  # Get the current time
  start_time=$(date +%s)

  # Calculate the value of x (20000 divided by n)
  x=$((30000 / n))

  # Loop from 1 to n, and run the command for each value
  for i in $(seq 1 $n); do
    echo "Executing: sudo ip link set ens6f1np1 vf $i max_tx_rate $x"
    sudo ip link set ens6f1np1 vf $i max_tx_rate $x
  done

  # Get the current time again, after running the commands
  end_time=$(date +%s)

  # Calculate how long the commands took to run
  elapsed_time=$((end_time - start_time))

  # Sleep for the remaining time, if any
  if [ $elapsed_time -lt 60 ]; then
    sleep_time=$((60 - elapsed_time))
    sleep $sleep_time
  fi

  echo "Done! Waiting for the next iteration..."
done

echo "All iterations completed!"
