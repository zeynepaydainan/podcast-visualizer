#!/bin/bash
# test_cloud.sh
# Verifies that the deployed Cloud Run agent service endpoint is reachable and responding.

set -e

ENDPOINT_URL="${1:-$CLOUD_RUN_ENDPOINT_URL}"

if [ -z "$ENDPOINT_URL" ]; then
    echo "Error: Deployed endpoint URL is not set."
    echo "Usage: ./test_cloud.sh <ENDPOINT_URL>"
    echo "Or set the environment variable: export CLOUD_RUN_ENDPOINT_URL=<ENDPOINT_URL>"
    exit 1
fi

echo "Testing deployed endpoint at: $ENDPOINT_URL"

# Send a request to the endpoint to check accessibility.
status_code=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT_URL")

echo "Response status code: $status_code"

if [ "$status_code" -eq 200 ] || [ "$status_code" -eq 307 ] || [ "$status_code" -eq 302 ]; then
    echo "========================================================="
    echo "SUCCESS: The deployed endpoint is up and responding!"
    echo "========================================================="
else
    echo "========================================================="
    echo "FAILURE: The deployed endpoint returned status: $status_code"
    echo "========================================================="
    exit 1
fi
