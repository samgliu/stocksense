#!/bin/bash

# Load environment variables from .env
set -o allexport
source .env
set +o allexport

# Create or update Docker registry secret for GHCR
echo "📦 Creating ghcr-secret..."
kubectl delete secret ghcr-secret --ignore-not-found
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username="$GITHUB_USER" \
  --docker-password="$GHCR_PAT" \
  --docker-email="$GITHUB_EMAIL"

# Create or update Firebase credentials secret
echo "🔐 Creating firebase-credentials..."
kubectl delete secret firebase-credentials --ignore-not-found
kubectl create secret generic firebase-credentials \
  --from-file=serviceAccountKey.json="$SERVICE_ACCOUNT_KEY_PATH"

echo "✅ All secrets created or updated."