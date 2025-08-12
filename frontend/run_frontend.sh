#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d node_modules ]; then
  echo "Installing frontend deps..."
  npm ci || npm install
fi

echo "Starting Vite dev server on http://localhost:5173"
npm run dev