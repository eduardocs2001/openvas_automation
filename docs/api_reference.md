# API Reference & Script Usage

## `scripts/run_scan.py`

This script automates the process of creating a target, creating a task, running a scan, and reporting the results to a webhook.

### Arguments

| Argument | Description | Default | Required |
|----------|-------------|---------|----------|
| `--socket` | Path to the GVMD socket | `/run/gvmd/gvmd.sock` | No |
| `--user` | GVM Username | - | Yes |
| `--password` | GVM Password | - | Yes |
| `--target-ip` | IP address or hostname to scan | - | Yes |
| `--target-name` | Name for the target in OpenVAS | `Automated Target` | No |
| `--task-name` | Name for the scan task | `Automated Scan` | No |
| `--webhook-url` | URL to send the JSON report to | - | No |

### Workflow

1. **Connect:** Establishes connection to GVMD via Unix Socket.
2. **Authenticate:** Logs in with provided credentials.
3. **Setup:**
   - checks/creates Target.
   - checks/creates Task (using "Full and Fast" config).
4. **Scan:** Starts the task and monitors progress.
5. **Report:**
   - Retrieves the report ID.
   - Fetches the report content (attempts to get JSON or falls back to XML).
6. **Integration:** Sends the report payload to the specified Webhook URL.

### JSON Payload Structure

The payload sent to n8n has the following structure:

```json
{
  "scan_id": "task-uuid",
  "report_id": "report-uuid",
  "report_content": "<xml>...</xml> OR {json_content}"
}
```
