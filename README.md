# OpenVAS Automation & n8n Integration Pipeline

This project provides an automated pipeline for Vulnerability Analysis using OpenVAS (Greenbone Vulnerability Management) via Docker, with automated scans via CLI and integration of results into n8n.

## Documentation

- **[Installation Guide](docs/installation.md)**: Instructions on how to set up the environment, configure OpenVAS, and start the services.
- **[API & Script Reference](docs/api_reference.md)**: Detailed usage of the automation script and API explanations.

## Quick Start

1. **Start Services:**
   ```bash
   docker compose up -d
   ```

2. **Setup Admin User:**
   ```bash
   ./scripts/setup_openvas.sh
   ```

3. **Run a Scan:**
   (Run from inside the `gvm-tools` container for easiest socket access)
   ```bash
   # Install dependencies inside container first
   docker compose exec -u 0 gvm-tools pip install requests

   # Copy script to container
   docker compose cp scripts/run_scan.py gvm-tools:/run_scan.py

   # Run scan
   docker compose exec gvm-tools python3 /run_scan.py --user admin --password <password> --target-ip scanme.nmap.org --webhook-url http://n8n:5678/webhook/scan-report
   ```

## Project Structure

```
.
├── docker-compose.yml       # OpenVAS and n8n orchestration
├── scripts/
│   ├── setup_openvas.sh     # Initial setup script
│   ├── run_scan.py          # Main automation script (Python)
│   └── requirements.txt     # Python dependencies
├── docs/
│   ├── installation.md      # Detailed installation guide
│   └── api_reference.md     # Script usage documentation
└── README.md
```

## Features

- **Infrastructure:** Fully containerized OpenVAS and n8n using Docker Compose.
- **Automation:** Python script using `python-gvm` to control OpenVAS (Target creation, Task creation, Scan execution).
- **Integration:** Automated reporting of scan results to n8n Webhook.
- **Data:** Retrieves reports (XML/JSON) and forwards them for further processing.

## Integration Details

The project uses a Python script (`scripts/run_scan.py`) instead of native OpenVAS Alerts for greater flexibility. The script:
1. Connects to the GVMD socket.
2. Creates or reuses a Target and Task.
3. Triggers the Scan.
4. Monitors the Scan status until completion.
5. Downloads the report (falling back to XML if JSON format is not configured/available).
6. Pushes the report payload to an n8n Webhook.

## Requirements

- Docker & Docker Compose
- Python 3.9+ (if running scripts locally)
