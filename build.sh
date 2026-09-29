#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=== Installing Python dependencies ==="
pip install -r backend/requirements.txt

echo "=== Seeding Demo Database ==="
python backend/seed_demo.py

echo "=== Building React Frontend Assets ==="
if command -v npm &> /dev/null
then
    cd frontend
    npm install
    npm run build
    cd ..
    mkdir -p backend/static
    cp -r frontend/dist/* backend/static/
    echo "Frontend build copied to backend/static/"
else
    echo "npm not found; using existing backend/static assets."
fi

echo "=== Build Complete ==="
