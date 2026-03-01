"""
DigitalOcean Functions: Low-Stock Alert Email Sender

Triggered by HTTP POST from the backend API when an item's quantity
drops below its low_stock_threshold.

Expected payload (sent by alert_service.py):
{
    "item_name": "Arduino Uno R3",
    "sku": "ELEC-001",
    "quantity": 5,
    "threshold": 20,
    "location": "Warehouse A",
    "recipient_emails": ["manager@example.com"]
}

Deploy:
    doctl serverless deploy serverless/

Test:
    curl -X POST <function-url> \
      -H "Content-Type: application/json" \
      -d '{"item_name":"Test Item","sku":"TEST-001","quantity":3,"threshold":10,"location":"Warehouse A","recipient_emails":["you@example.com"]}'
"""

import json
import os
import urllib.request
import urllib.error


def main(args: dict) -> dict:
    """Handle low-stock alert notification via SendGrid email."""

    # Validate required fields
    required = ["item_name", "sku", "quantity", "threshold", "recipient_emails"]
    for field in required:
        if field not in args:
            return {
                "statusCode": 400,
                "body": {"error": f"Missing required field: {field}"},
            }

    item_name = args["item_name"]
    sku = args["sku"]
    quantity = args["quantity"]
    threshold = args["threshold"]
    location = args.get("location", "Unknown")
    recipient_emails = args["recipient_emails"]

    if not recipient_emails:
        return {
            "statusCode": 400,
            "body": {"error": "No recipient emails provided"},
        }

    # Read config from environment or function parameters
    sendgrid_api_key = os.environ.get(
        "SENDGRID_API_KEY", args.get("SENDGRID_API_KEY", "")
    )
    from_email = os.environ.get(
        "ALERT_FROM_EMAIL", args.get("ALERT_FROM_EMAIL", "alerts@inventory-app.com")
    )

    if not sendgrid_api_key:
        return {
            "statusCode": 500,
            "body": {"error": "SendGrid API key not configured"},
        }

    # Build email content
    subject = f"Low Stock Alert: {item_name} ({sku})"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #dc3545; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0;">&#9888; Low Stock Alert</h1>
        </div>
        <div style="padding: 20px; background-color: #f8f9fa; border: 1px solid #dee2e6;">
            <h2 style="color: #dc3545; margin-top: 0;">{item_name}</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>SKU:</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{sku}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Current Quantity:</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6; color: #dc3545; font-weight: bold;">{quantity}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Threshold:</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{threshold}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Location:</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{location}</td>
                </tr>
            </table>
            <p style="margin-top: 20px; color: #6c757d; font-size: 14px;">
                This is an automated alert from the Inventory Management System.
                Please restock this item as soon as possible.
            </p>
        </div>
        <div style="padding: 10px; text-align: center; color: #6c757d; font-size: 12px;">
            Inventory Management System &mdash; ECE 1779
        </div>
    </div>
    """

    # Send emails via SendGrid REST API (using stdlib only — no external deps)
    sent_count = 0
    errors = []

    for email in recipient_emails:
        payload = {
            "personalizations": [{"to": [{"email": email}]}],
            "from": {"email": from_email, "name": "Inventory Alerts"},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_content}],
        }

        req = urllib.request.Request(
            "https://api.sendgrid.com/v3/mail/send",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {sendgrid_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            urllib.request.urlopen(req)
            sent_count += 1
            print(f"Email sent to {email}")
        except urllib.error.HTTPError as e:
            error_msg = f"Failed to send to {email}: {e.code}"
            print(error_msg)
            errors.append(error_msg)

    if sent_count == 0:
        return {
            "statusCode": 500,
            "body": {"error": "Failed to send any emails", "details": errors},
        }

    return {
        "statusCode": 200,
        "body": {
            "message": f"Alerts sent to {sent_count}/{len(recipient_emails)} recipient(s)",
            "item": item_name,
            "sku": sku,
        },
    }
