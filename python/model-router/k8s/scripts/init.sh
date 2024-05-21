#!/bin/bash

# Loop over all YAML files in the current directory
for file in *.yaml; do
    echo "Applying $file to the cluster..."

    # Apply the YAML file
    kubectl apply -f "$file"

    # Check the status and print the result
    if [ $? -eq 0 ]; then
        echo "Successfully applied $file"
    else
        echo "Failed to apply $file. Please check the file for errors."
    fi
    echo "" # Print a blank line for better readability
done

echo "All YAML files in the current directory have been processed."