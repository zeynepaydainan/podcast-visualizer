#!/bin/bash
# deploy.sh
# Deploys the podcast-visualizer agent to Google Cloud Run.
# Reads project ID from the first argument or CLOUD_RUN_PROJECT_ID env var.
# Does NOT run automatically.

set -e

PROJECT_ID="${1:-$CLOUD_RUN_PROJECT_ID}"
REGION="${2:-us-central1}"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: Google Cloud Project ID is not set."
    echo "Usage: ./deploy.sh <PROJECT_ID> [REGION]"
    echo "Or set the environment variable: export CLOUD_RUN_PROJECT_ID=<PROJECT_ID>"
    exit 1
fi

echo "========================================================="
echo "Podcast Visualizer - Cloud Run Deployment"
echo "========================================================="
echo "Project ID: $PROJECT_ID"
echo "Region:     $REGION"
echo ""
echo "Prerequisites:"
echo "1. Install Google Cloud SDK (gcloud CLI)"
echo "2. Authenticate: gcloud auth login"
echo "3. Enable Billing on the project"
echo "4. Enable APIs: Cloud Run, Cloud Build, Artifact Registry"
echo "========================================================="
echo ""

read -p "Do you want to proceed with the deployment? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Set the active project
gcloud config set project "$PROJECT_ID"

echo "Deploying via ADK CLI to Cloud Run..."
.venv/bin/adk deploy cloud_run \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --service_name="podcast-visualizer" \
  --with_ui \
  agent/

echo "========================================================="
echo "Deployment initiated successfully!"
echo "========================================================="
