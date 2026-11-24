import base64

from app.services.gmail_normalizer import (
    MAX_BODY_CHARS,
    MAX_MIME_DEPTH,
    _walk_parts,
    classify_gmail_content,
    normalize_gmail_message,
)


def test_sync_classifier_categorizes_common_mail_types():
    assert classify_gmail_content("Summer Internship application received", "", "", "") == "internship"
    assert classify_gmail_content("Interview invitation", "", "talent@company.test", "") == "interview"
    assert classify_gmail_content("University semester update", "", "", "") == "college"
    assert classify_gmail_content("Security alert: new sign-in", "", "", "") == "important"
    assert classify_gmail_content("Limited time discount", "", "", "") == "promotions"
    assert classify_gmail_content("Your package shipment update", "", "", "") == "updates"


def test_malformed_and_deep_mime_tree_is_bounded_and_normalizes_safely():
    root = {"mimeType": "multipart/mixed", "parts": []}
    current = root
    for _ in range(MAX_MIME_DEPTH + 100):
        child = {"mimeType": "multipart/mixed", "parts": []}
        current["parts"].append(child)
        current = child

    assert len(list(_walk_parts(root))) <= MAX_MIME_DEPTH + 1
    normalized = normalize_gmail_message({
        "id": "message-1",
        "threadId": "thread-1",
        "payload": "malformed payload shape",
        "snippet": "Untrusted snippet text",
    }, user_id=5, connected_account_id=9)
    assert normalized["body"] == "Untrusted snippet text"
    assert normalized["subject"] == "(no subject)"


def test_message_body_budget_and_invalid_attachment_size_are_bounded():
    body = "x" * (MAX_BODY_CHARS + 200)
    encoded = base64.urlsafe_b64encode(body.encode()).decode().rstrip("=")
    normalized = normalize_gmail_message({
        "id": "message-2",
        "threadId": "thread-2",
        "payload": {
            "mimeType": "multipart/mixed",
            "parts": [
                {"mimeType": "text/plain", "body": {"data": encoded}},
                {"filename": "bad-size.txt", "mimeType": "text/plain", "body": {"size": "not-an-integer"}},
            ],
        },
    }, user_id=5, connected_account_id=9)
    assert len(normalized["body"]) == MAX_BODY_CHARS
    assert normalized["attachments"][0]["size"] == 0
