#!/bin/bash
# cpu_monitor.sh - Show CPU usage %

# 取 1 秒内的整体 CPU 使用率（user+system），输出百分比
CPU_USAGE=$(LC_ALL=C top -bn1 | awk '/^%Cpu\(s\):/ {print 100 - $8}')

echo "=== CPU Monitor ==="
echo "Time: $(date '+%F %T')"
printf "CPU Usage: %.1f%%\n" "$CPU_USAGE"
