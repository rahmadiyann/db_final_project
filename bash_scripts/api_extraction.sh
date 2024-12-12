#!/bin/bash

# Check if both arguments are provided
if [ $# -ne 3 ]; then
    echo "Usage: $0 <timestamp_ms> <output_path>"
    exit 1
fi

timestamp=$1
dir_path=$2
file_name=$3

# Create output directory if it doesn't exist
mkdir -p "$dir_path"

# Make API call and save response
response=$(curl -s "http://flask:8000/recent_played?last_fetch_time=$timestamp&limit=50")

echo "Response: $response"

if [ $? -ne 0 ]; then
    echo "Error: Failed to call API"
    exit 1
fi

# Save to JSON file
echo "$response" > "$dir_path/$file_name"

if [ $? -ne 0 ]; then
    echo "Error: Failed to save JSON file"
    exit 1
fi