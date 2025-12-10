import argparse
import time
import sys
import json
import requests
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeTransform
from gvm.xml import pretty_print

def connect_gvm(socket_path):
    connection = UnixSocketConnection(path=socket_path)
    transform = EtreeTransform()
    gmp = Gmp(connection, transform=transform)
    return gmp

def create_target(gmp, name, hosts):
    # Check if target exists
    targets = gmp.get_targets(filter=f"name={name}")
    if int(targets.xpath('//@count')[0]) > 0:
        print(f"Target '{name}' already exists.")
        target_id = targets.xpath('//target/@id')[0]
        return target_id

    response = gmp.create_target(name=name, hosts=[hosts], port_list_id="33d0cd82-57c6-11e1-8ed1-406186ea4fc5") # Default port list
    target_id = response.xpath('//@id')[0]
    print(f"Created target '{name}' with ID: {target_id}")
    return target_id

def create_task(gmp, name, target_id, scanner_id):
    # Check if task exists
    tasks = gmp.get_tasks(filter=f"name={name}")
    if int(tasks.xpath('//@count')[0]) > 0:
        print(f"Task '{name}' already exists.")
        task_id = tasks.xpath('//task/@id')[0]
        return task_id

    # Using Full and Fast config by default
    config_id = "daba56c8-73ec-11df-a475-002264764cea"

    response = gmp.create_task(name=name, config_id=config_id, target_id=target_id, scanner_id=scanner_id)
    task_id = response.xpath('//@id')[0]
    print(f"Created task '{name}' with ID: {task_id}")
    return task_id

def start_scan(gmp, task_id):
    response = gmp.start_task(task_id)
    report_id = response.xpath('//report_id/text()')[0]
    print(f"Started scan for task {task_id}. Report ID: {report_id}")
    return report_id

def monitor_scan(gmp, task_id):
    while True:
        task = gmp.get_task(task_id)
        status = task.xpath('//status/text()')[0]
        progress = task.xpath('//progress/text()')[0]
        print(f"Scan status: {status} - Progress: {progress}%")

        if status == 'Done':
            break
        elif status == 'Stopped' or status == 'New' or status == 'Interrupted':
             # Handle other terminal states if necessary or 'New' if it fails to start immediately
             if status != 'New':
                 break

        time.sleep(10)

def get_report(gmp, report_id):
    # Get report format id for JSON - this might vary, usually we get XML and convert or request specific format
    # Anonymous XML report format ID: 5057e5cc-b825-11e4-9d0e-28d24461215b
    # Use standard XML and convert to JSON in python or request a JSON report format if available.
    # Greenbone often has a JSON format plugin.

    # List formats to find JSON
    formats = gmp.get_report_formats()
    json_format_id = None
    for fmt in formats.xpath('//report_format'):
        if 'JSON' in fmt.xpath('name/text()')[0]:
            json_format_id = fmt.xpath('@id')[0]
            break

    if not json_format_id:
        print("JSON report format not found. Falling back to XML.")
        response = gmp.get_report(report_id)
        return response

    # If JSON format exists, request the report in that format.
    response = gmp.get_report(report_id, report_format_id=json_format_id)
    return response

def send_webhook(url, data):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print(f"Report sent to webhook. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Failed to send report to webhook: {e}")

def main():
    parser = argparse.ArgumentParser(description="OpenVAS Automation Script")
    parser.add_argument("--socket", default="/run/gvmd/gvmd.sock", help="Path to GVMD socket")
    parser.add_argument("--user", required=True, help="GVM Username")
    parser.add_argument("--password", required=True, help="GVM Password")
    parser.add_argument("--target-ip", required=True, help="Target IP address")
    parser.add_argument("--target-name", default="Automated Target", help="Name of the target")
    parser.add_argument("--task-name", default="Automated Scan", help="Name of the task")
    parser.add_argument("--webhook-url", help="URL of the n8n webhook")

    args = parser.parse_args()

    try:
        gmp = connect_gvm(args.socket)
        gmp.authenticate(args.user, args.password)

        # Get OpenVAS Scanner ID
        scanners = gmp.get_scanners()
        scanner_id = None
        for scanner in scanners.xpath('//scanner'):
            if scanner.xpath('name/text()')[0] == "OpenVAS Default":
                scanner_id = scanner.xpath('@id')[0]
                break

        if not scanner_id:
             # Fallback to first available or error
             scanner_id = scanners.xpath('//scanner/@id')[0]

        target_id = create_target(gmp, args.target_name, args.target_ip)
        task_id = create_task(gmp, args.task_name, target_id, scanner_id)
        report_id = start_scan(gmp, task_id)

        monitor_scan(gmp, task_id)

        report = get_report(gmp, report_id)

        if args.webhook_url:
            from lxml import etree
            import base64

            report_content = ""

            if isinstance(report, str):
                report_content = report
            else:
                 # Attempt to extract text content from the report element
                 report_elem = report.find('.//report')
                 if report_elem is not None and report_elem.text:
                    report_content = report_elem.text
                 else:
                     # Fallback: just send the XML string
                     report_content = etree.tostring(report, pretty_print=True).decode()

            payload = {
                "scan_id": task_id,
                "report_id": report_id,
                "report_content": report_content
            }
            send_webhook(args.webhook_url, payload)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
