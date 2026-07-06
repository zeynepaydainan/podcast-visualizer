#!/bin/bash
# test_local.sh
# Scripted end-to-end check: runs the full multi-agent pipeline once
# (via run_pipeline.py) and verifies the visual summary file was created.
set -e
 
echo "Starting local end-to-end check..."
 
# Preconditions: transcript must exist.
if [ ! -f "data/episodes/insulin-pcos-101.txt" ]; then
  echo "Error: Transcript file not found at data/episodes/insulin-pcos-101.txt"
  exit 1
fi
 
# Clean up any previous summary so we verify a fresh run.
rm -f data/summaries/insulin-pcos-101.html
 
# Run the pipeline with the venv's Python (same interpreter as the agent
# and, via sys.executable, the MCP server subprocess).
.venv/bin/python3 -u run_pipeline.py
 
# Verify the summary was generated.
if [ -f "data/summaries/insulin-pcos-101.html" ]; then
  echo "========================================================="
  echo "SUCCESS: Visual summary generated at data/summaries/insulin-pcos-101.html"
  echo "========================================================="
else
  echo "========================================================="
  echo "FAILURE: Visual summary was not generated."
  echo "========================================================="
  exit 1
fi