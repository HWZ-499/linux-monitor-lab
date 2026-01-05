#!/bin/bash
# mem_monitor.sh - Show memory usage (from /proc/meminfo)

MEMTOTAL_KB=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
MEMAVAILABLE_KB=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)

# 兼容极少数系统没有 MemAvailable 的情况
if [ -z "$MEMAVAILABLE_KB" ] || [ "$MEMAVAILABLE_KB" -eq 0 ]; then
  MEMFREE_KB=$(awk '/^MemFree:/ {print $2}' /proc/meminfo)
  BUFFERS_KB=$(awk '/^Buffers:/ {print $2}' /proc/meminfo)
  CACHED_KB=$(awk '/^Cached:/ {print $2}' /proc/meminfo)
  MEMAVAILABLE_KB=$((MEMFREE_KB + BUFFERS_KB + CACHED_KB))
fi

USED_KB=$((MEMTOTAL_KB - MEMAVAILABLE_KB))

TOTAL_MB=$((MEMTOTAL_KB / 1024))
USED_MB=$((USED_KB / 1024))
AVAIL_MB=$((MEMAVAILABLE_KB / 1024))

USAGE=$(awk -v u="$USED_KB" -v t="$MEMTOTAL_KB" 'BEGIN {printf "%.1f", (u/t)*100}')

echo "=== Memory Monitor ==="
echo "Time: $(date '+%F %T')"
echo "Total: ${TOTAL_MB} MB"
echo "Used : ${USED_MB} MB"
echo "Avail: ${AVAIL_MB} MB"
echo "Usage: ${USAGE}%"

