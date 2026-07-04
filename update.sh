#!/usr/bin/env bash
# Update the deployed bot to match the vps-deployment branch, then restart.
# Location-independent: operates on whatever repo this script lives in.
set -euo pipefail

SERVICE="${SERVICE:-vocab}"          # override: SERVICE=myname ./update.sh
BRANCH="${BRANCH:-vps-deployment}"

cd "$(dirname "$(readlink -f "$0")")"   # repo root = this script's dir

git fetch origin
git reset --hard "origin/${BRANCH}"     # matches the force-pushed branch exactly
sudo systemctl restart "$SERVICE"

echo "updated to $(git rev-parse --short HEAD) on ${BRANCH}, restarted ${SERVICE}"
