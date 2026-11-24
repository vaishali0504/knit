import base64
from datetime import datetime, timezone
from email.header import decode_header, make_header
from email.utils import getaddresses, parsedate_to_datetime
from html.parser import HTMLParser
from typing import Any


MAX_BODY_CHARS = 1_000_000
MAX_MIME_PARTS = 1000
MAX_MIME_DEPTH = 50


def classify_gmail_content(subject: str, sender_name: str, sender_email: str, body: str) -> str:
    text = " ".join((subject, sender_name, sender_email, body)).lower()
    if any(word in text for word in ("internship", "summer intern", "winter intern", "intern role", "graduate trainee")):
        return "internship"
    if any(word in text for word in ("interview", "coding round", "assessment round", "hr round", "recruiter", "hiring")) or "talent@" in text:
        return "interview"
    if any(word in text for word in ("college", "university", "campus", "admission", "semester", "student", "coursework")):
        return "college"
    if any(word in text for word in ("security alert", "password changed", "sign-in", "login alert", "account activity", "important:")):
        return "important"
    if any(word in text for word in ("sale", "discount", "offer", "coupon", "deal", "promotion", "limited time")):
        return "promotions"
    if any(word in text for word in ("invoice", "receipt", "payment", "subscription", "statement", "delivery", "shipment", "order")):
        return "updates"
    if any(word in text for word in ("verify immediately", "urgent action", "phishing", "reset password", "confirm account", "gift card")):
        return "suspicious"
    if any(word in text for word in ("family", "friend", "personal", "dinner", "birthday")):
        return "personal"
    return "other"


class _HTMLText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _decode_header(value: str | None) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except (LookupError, UnicodeError, ValueError):
        return value


def _headers(payload: dict[str, Any]) -> dict[str, str]:
    root = payload.get("payload")
    if not isinstance(root, dict):
        return {}
    raw = root.get("headers", [])
    if not isinstance(raw, list):
        return {}
    result: dict[str, str] = {}
    for item in raw:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            key = item["name"].lower()
            result[key] = _decode_header(str(item.get("value", "")))
    return result


def _decode_data(value: str | None, limit: int = MAX_BODY_CHARS) -> str:
    if not value:
        return ""
    try:
        # Decode only enough base64 input to fill the remaining output budget.
        bounded = value[: ((max(limit, 0) + 2) // 3) * 4]
        decoded = base64.urlsafe_b64decode(bounded + "=" * (-len(bounded) % 4))
        return decoded.decode("utf-8", errors="replace")[:max(limit, 0)]
    except (ValueError, TypeError):
        return ""


def _walk_parts(part: dict[str, Any]):
    stack = [(part, 0)]
    visited = 0
    while stack and visited < MAX_MIME_PARTS:
        current, depth = stack.pop()
        if not isinstance(current, dict):
            continue
        visited += 1
        yield current
        children = current.get("parts", [])
        if depth < MAX_MIME_DEPTH and isinstance(children, list):
            stack.extend((child, depth + 1) for child in reversed(children) if isinstance(child, dict))


def _body(payload: dict[str, Any], snippet: str) -> str:
    root = payload.get("payload", {})
    if not isinstance(root, dict):
        return snippet[:MAX_BODY_CHARS]
    plain: list[str] = []
    html: list[str] = []
    remaining = MAX_BODY_CHARS
    for part in _walk_parts(root):
        if remaining <= 0:
            break
        mime = part.get("mimeType")
        data = part.get("body", {}).get("data") if isinstance(part.get("body"), dict) else None
        if mime == "text/plain" and data:
            text = _decode_data(data, remaining)
            plain.append(text)
            remaining -= len(text)
        elif mime == "text/html" and data:
            text = _decode_data(data, remaining)
            html.append(text)
            remaining -= len(text)
    if plain:
        return "\n".join(plain)[:MAX_BODY_CHARS]
    if html:
        parser = _HTMLText()
        parser.feed("\n".join(html))
        return " ".join(" ".join(parser.parts).split())[:MAX_BODY_CHARS]
    return snippet[:MAX_BODY_CHARS]


def _timestamp(message: dict[str, Any], headers: dict[str, str]) -> datetime:
    try:
        milliseconds = int(message.get("internalDate"))
        return datetime.fromtimestamp(milliseconds / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OSError, OverflowError):
        try:
            parsed = parsedate_to_datetime(headers.get("date", ""))
            return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
        except (TypeError, ValueError, OverflowError):
            return datetime.now(timezone.utc)


def normalize_gmail_message(message: dict[str, Any], user_id: int, connected_account_id: int) -> dict[str, Any]:
    message_id = message.get("id")
    thread_id = message.get("threadId")
    if not isinstance(message_id, str) or not message_id or not isinstance(thread_id, str) or not thread_id:
        raise ValueError("Gmail message is missing provider identifiers")
    headers = _headers(message)
    sender_values = getaddresses([headers.get("from", "")])
    sender_name, sender_email = sender_values[0] if sender_values else ("", "")
    sender_email = sender_email[:255]
    sender_name = (_decode_header(sender_name).strip() or sender_email)[:255]
    recipients = [address for _, address in getaddresses([
        headers.get("to", ""), headers.get("cc", ""), headers.get("bcc", ""),
    ]) if address]
    recipient = ", ".join(recipients)[:255] or "undisclosed-recipients"
    labels = message.get("labelIds", [])
    labels = labels if isinstance(labels, list) else []
    snippet = message.get("snippet") if isinstance(message.get("snippet"), str) else ""
    attachments = []
    root = message.get("payload", {})
    if isinstance(root, dict):
        for part in _walk_parts(root):
            filename = part.get("filename")
            part_body = part.get("body", {})
            if filename and isinstance(part_body, dict):
                try:
                    size = max(0, min(int(part_body.get("size", 0) or 0), 2_147_483_647))
                except (TypeError, ValueError, OverflowError):
                    size = 0
                attachments.append({
                    "filename": str(filename)[:255],
                    "mime_type": str(part.get("mimeType", "application/octet-stream"))[:255],
                    "size": size,
                    "provider_attachment_id": str(part_body.get("attachmentId", ""))[:512],
                })
    subject = (headers.get("subject") or "(no subject)")[:500]
    body = _body(message, snippet)
    category = classify_gmail_content(
        subject,
        sender_name or "Unknown sender",
        sender_email or "unknown@invalid.local",
        body,
    )
    return {
        "user_id": user_id,
        "connected_account_id": connected_account_id,
        "provider_message_id": message_id[:255],
        "provider_thread_id": thread_id[:255],
        "sender_name": sender_name or "Unknown sender",
        "sender_email": sender_email or "unknown@invalid.local",
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "received_at": _timestamp(message, headers),
        "category": category,
        "is_read": "UNREAD" not in labels,
        "is_important": "IMPORTANT" in labels,
        "attachments": attachments,
    }
