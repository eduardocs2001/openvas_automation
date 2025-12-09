#!/bin/bash

# setup_openvas.sh
# This script helps setting up the initial admin user and downloading feeds if not done.
# It relies on the docker-compose setup.

echo "Setting up OpenVAS..."

# Check if docker-compose is running
if ! docker compose ps | grep -q "Up"; then
    echo "Docker containers are not running. Starting them..."
    docker compose up -d
    echo "Waiting for services to initialize..."
    sleep 30
fi

# Create/Update Admin User
echo "Creating/Updating admin user..."
read -p "Enter username (default: admin): " GVM_USER
GVM_USER=${GVM_USER:-admin}
read -s -p "Enter password: " GVM_PASS
echo ""

docker compose exec -u gvmd gvmd gvmd --user="$GVM_USER" --new-password="$GVM_PASS"

echo "User updated."

# Display info
echo "Greenbone Security Assistant should be available at http://127.0.0.1:9392"
echo "You can now run the scan script using:"
echo "python3 scripts/run_scan.py --user $GVM_USER --password <password> --target-ip <ip>"
