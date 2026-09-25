"""
AegisGraph — Session Ticket Issuer/Verifier.

A ticket is a server-signed token binding an audit-session id to the signed-in
user who owns it. It lets a user continue (or end) their own chat session; a
ticket presented by any other user is rejected. Role and risk state never come
from the ticket — they are looked up server-side from the authenticated user.

Format: base64url(json({"sid": ..., "uid": ..., "exp": ...})) + "." + hmac_hex
"""
import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Optional, Tuple

from app.core.config import settings

DEFAULT_TICKET_TTL_SECONDS = 4 * 60 * 60  # 4 hours


def _sign(payload_b64: str) -> str:
    key = settings.SECURITY_SESSION_SECRET.encode("utf-8")
    return hmac.new(key, payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()


def issue_ticket(user_id: str, session_id: Optional[str] = None, ttl_seconds: int = DEFAULT_TICKET_TTL_SECONDS) -> Tuple[str, str]:
    """Create a signed ticket for user_id. Returns (ticket, session_id)."""
    sid = session_id or str(uuid.uuid4())
    payload = {"sid": sid, "uid": user_id, "exp": time.time() + ttl_seconds}
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode("utf-8")
    return f"{payload_b64}.{_sign(payload_b64)}", sid


def verify_ticket(token: str, user_id: str) -> Optional[str]:
    """
    Return the session_id if the ticket is genuine, unexpired and owned by
    user_id; otherwise None (callers then start a fresh session).
    """
    if not token or "." not in token:
        return None

    payload_b64, _, signature = token.partition(".")
    if not hmac.compare_digest(signature, _sign(payload_b64)):
        return None

    try:
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8"))
        if payload["uid"] != user_id or time.time() > payload["exp"]:
            return None
        return payload["sid"]
    except (ValueError, KeyError, TypeError):
        return None
