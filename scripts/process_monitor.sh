#!/bin/bash
# process_monitor.sh - Show top processes by CPU and MEM

echo "=== Process Monitor (Top 5) ==="
echo "Time: $(date '+%F %T')"
echo

echo "[Top 5 by CPU]"
ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -n 6
echo

echo "[Top 5 by MEM]"
ps -eo pid,comm,%cpu,%mem --sort=-%mem | head -n 6
