#!/bin/bash
# process_detail.sh - Show process details by PID

PID="$1"

if [ -z "$PID" ]; then
  echo "ERROR: PID required"
  exit 1
fi

if ! ps -p "$PID" > /dev/null 2>&1; then
  echo "ERROR: PID not found"
  exit 1
fi

read -r COMMAND CPU MEM ELAPSED USER STAT <<< "$(ps -p "$PID" -o comm=,%cpu=,%mem=,etime=,user=,stat=)"

echo "PID: $PID"
echo "Command: $COMMAND"
echo "CPU: $CPU"
echo "Mem: $MEM"
echo "Elapsed: $ELAPSED"
echo "User: $USER"
echo "State: $STAT"
