
#!/bin/bash

# Function to get the cached memory usage in bytes
get_cached_memory_usage() {
    cached_memory=$(free | awk '/^Mem:/ {print $7}')
    echo "$cached_memory"
}

# Function to get the total memory usage in bytes
get_total_memory_usage() {
    total_memory=$(free | awk '/^Mem:/ {print $2}')
    echo "$total_memory"
}

# Check if the cached memory exceeds the threshold and restart if necessary
restart_if_cached_memory_exceeds_threshold() {
    threshold=$((1024 * 1024 * 1000))  # Threshold in bytes (1.2GB)

    cached_memory=$(get_cached_memory_usage)
    if [[ $cached_memory -gt $threshold ]]; then
        echo "Cached memory exceeds the threshold. Restarting the Raspberry Pi..."
        sudo reboot
    else
        echo "Cached memory is within the threshold. No restart required."
    fi
}

# Check if another instance of the script is already running
if pidof -x "$(basename "$0")" -o %PPID >/dev/null; then
    echo "Another instance of the script is already running. Exiting."
    exit 1
fi

# Get current time
current_time=$(date +%H:%M)

# Check if it's 22:30 (10:30 pm) or the "run-now" argument is provided
if [[ $current_time == "22:30" ]] || [[ $1 == "run-now" ]]; then
    echo "Checking cached memory usage..."
    restart_if_cached_memory_exceeds_threshold
else
    echo "Not the scheduled time or 'run-now' argument not provided. Exiting."
fi






