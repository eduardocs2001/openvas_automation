# Test Report: OpenVAS Automation & n8n Integration

## 1. Introduction
This document details the testing strategy and results for the OpenVAS Automation pipeline. Due to environment restrictions (network timeouts accessing Greenbone registry), the full End-to-End test could not be executed in the development sandbox. This report outlines the verification steps performed and the procedure for validation in the target environment.

## 2. Test Environment
- **Platform:** Docker Compose (Linux)
- **Services:**
  - Greenbone Community Edition (gvmd, ospd-openvas, redis, postgres, gsa)
  - n8n (Workflow Automation)
  - gvm-tools (CLI access)

## 3. Verification Steps

### 3.1. Static Analysis
- **Docker Compose:** Validated syntax using `docker compose config`. Structure correctly defines all required services, volumes, and networks.
- **Python Script (`run_scan.py`):** Verified Python syntax. Logic covers:
  - Connection to GVM Socket.
  - Creation/Check of Targets and Tasks.
  - Monitoring of Scan Progress.
  - Report Retrieval (JSON/XML fallback).
  - Webhook integration.
- **Shell Script (`setup_openvas.sh`):** Verified Bash syntax.

### 3.2. Intended End-to-End Test Procedure
*To be executed in the deployment environment.*

#### Step 1: Infrastructure Initialization
1. Run `docker compose up -d`.
2. Wait for feed synchronization (logs can be checked via `docker compose logs -f vulnerability-tests`).
3. Verify `gsa` is accessible at `http://localhost:9392`.

#### Step 2: Integration Test (The "Happy Path")
1. **Setup n8n:**
   - Start a workflow with a Webhook node (POST).
   - Copy the test URL.
2. **Run Automation:**
   - Execute the scan script:
     ```bash
     docker compose exec gvm-tools python3 /run_scan.py --user admin --password <password> --target-ip 127.0.0.1 --webhook-url <n8n_url>
     ```
3. **Validation:**
   - **Console Output:** Should show Target created -> Task created -> Scan started -> Progress updates -> Report sent.
   - **n8n:** Check the execution data in the n8n UI. It should contain the JSON payload with `scan_id`, `report_id`, and `report_content`.
   - **OpenVAS:** Check the web interface to see the completed scan task.

## 4. Known Limitations & Observations
- **Feed Sync Time:** The initial startup of Greenbone containers requires downloading significant data (NVTs, CERT, SCAP). This can take 30+ minutes depending on bandwidth.
- **Image Availability:** The `registry.community.greenbone.net` can sometimes be slow or rate-limited.
- **JSON Format:** The default OpenVAS installation might only provide XML reports by default. The script handles this by falling back to XML content if the JSON format plugin is not active.

## 5. Conclusion
The code implementation is complete and follows the architectural requirements. While live verification was blocked by network restrictions in the sandbox, the logic is sound and ready for deployment testing.
