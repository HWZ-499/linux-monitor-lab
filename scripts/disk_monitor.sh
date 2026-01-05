#!/bin/bash
# disk_monitor.sh - Show disk usage

DISK_INFO=$(df -h / | awk 'NR==2 {print $2, $3, $4, $5}')

TOTAL=$(echo $DISK_INFO | awk '{print $1}')
USED=$(echo $DISK_INFO | awk '{print $2}')
AVAIL=$(echo $DISK_INFO | awk '{print $3}')
USAGE=$(echo $DISK_INFO | awk '{print $4}')

echo "=== Disk Monitor (/) ==="
echo "Time: $(date '+%F %T')"
echo "Total: $TOTAL"
echo "Used : $USED"
echo "Avail: $AVAIL"
echo "Usage: $USAGE"
