import httpx

from app.config import settings


def _build_subject(event: dict) -> str:
    event_type = event.get("type", "")
    name = event.get("name", "Unknown Item")

    if event_type == "low_stock_alert":
        return f"Low Stock Alert: {name}"
    elif event_type == "item_restocked":
        return f"Item Restocked: {name}"
    elif event_type == "item_withdrawn":
        return f"Item Withdrawn: {name}"
    return f"Inventory Notification: {name}"


def _build_body(event: dict) -> str:
    event_type = event.get("type", "")
    name = event.get("name", "Unknown Item")

    if event_type == "low_stock_alert":
        return (
            f"Low Stock Alert\n\n"
            f"Item: {name} (SKU: {event.get('sku', 'N/A')})\n"
            f"Current Quantity: {event.get('quantity', 'N/A')}\n"
            f"Threshold: {event.get('threshold', 'N/A')}\n"
            f"Location: {event.get('location', 'N/A')}\n"
        )
    elif event_type == "item_restocked":
        return (
            f"Item Restocked\n\n"
            f"Item: {name}\n"
            f"Quantity: {event.get('quantity_before', '?')} -> {event.get('quantity_after', '?')}\n"
            f"Notes: {event.get('notes', 'N/A')}\n"
        )
    elif event_type == "item_withdrawn":
        return (
            f"Item Withdrawn\n\n"
            f"Item: {name}\n"
            f"Quantity: {event.get('quantity_before', '?')} -> {event.get('quantity_after', '?')}\n"
            f"Notes: {event.get('notes', 'N/A')}\n"
        )
    return f"Inventory event: {event}"


def send_event_emails(emails: list[str], event: dict):
    """Send email notifications for an inventory event."""
    if not settings.sendgrid_api_key:
        print(f"[Email] Would notify {emails} about {event.get('type')}: {event.get('name')}")
        return

    subject = _build_subject(event)
    body = _build_body(event)

    for email in emails:
        try:
            httpx.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {settings.sendgrid_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "personalizations": [{"to": [{"email": email}]}],
                    "from": {"email": settings.alert_from_email},
                    "subject": subject,
                    "content": [{"type": "text/plain", "value": body}],
                },
                timeout=10.0,
            )
        except Exception as e:
            print(f"[Email] Failed to send to {email}: {repr(e)}")
