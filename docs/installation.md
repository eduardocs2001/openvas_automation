# OpenVAS Automation & n8n Integration - Installation Guide

## Prerequisites
- Docker
- Docker Compose
- Python 3.9+ (for the automation script)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Start the services:**
   This command pulls the Greenbone Community Containers and n8n, and starts them.
   ```bash
   docker compose up -d
   ```
   *Note: The first startup may take a significant amount of time as it downloads and syncs vulnerability feeds.*

3. **Verify Services:**
   - Greenbone Security Assistant (GSA): [http://localhost:9392](http://localhost:9392)
   - n8n: [http://localhost:5678](http://localhost:5678)

## Initial Configuration

### OpenVAS
1. **Set Admin Password:**
   You can use the helper script to set up the admin user.
   ```bash
   ./scripts/setup_openvas.sh
   ```
   Or manually:
   ```bash
   docker compose exec -u gvmd gvmd gvmd --user=admin --new-password='yourpassword'
   ```

### n8n
1. Open n8n at [http://localhost:5678](http://localhost:5678).
2. Create a new workflow.
3. Add a **Webhook** node.
   - Method: POST
   - Path: `webhook` (or any path you prefer)
   - Copy the Test URL (e.g., `http://localhost:5678/webhook-test/webhook`) or Production URL.
4. Activate the workflow.

## Running a Scan

1. **Install Python Dependencies:**
   ```bash
   pip install -r scripts/requirements.txt
   ```

2. **Run the Automation Script:**
   ```bash
   python3 scripts/run_scan.py \
     --user admin \
     --password <yourpassword> \
     --target-ip <target-ip> \
     --webhook-url <n8n-webhook-url>
   ```

   Example:
   ```bash
   python3 scripts/run_scan.py \
     --user admin \
     --password password123 \
     --target-ip scanme.nmap.org \
     --webhook-url http://localhost:5678/webhook/scan-report
   ```

   **Note:** If running the script from the host, ensure the `gvmd` socket is accessible. By default, the `docker-compose.yml` mounts the socket volume but it is not directly exposed to the host filesystem unless mapped.

   **Recommended approach for this setup:**
   The `gvm-tools` container has `gvm-tools` installed. We can install `requests` there and run the script.

   ```bash
   docker compose exec -u 0 gvm-tools pip install requests
   docker compose cp scripts/run_scan.py gvm-tools:/run_scan.py
   docker compose exec gvm-tools python3 /run_scan.py --user admin --password <pass> --target-ip scanme.nmap.org --webhook-url http://n8n:5678/webhook/scan-result
   ```
   (Note: usage of `n8n` hostname if running inside docker network)
