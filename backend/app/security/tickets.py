"""
AegisGraph — Session Ticket Issuer/Verifier.

Issues a tamper-proof, server-signed "ticket" binding a session_id to a role.
Chat requests must present this ticket to continue an existing session; the
role and session identity are always read from the verified ticket, never
from a client-supplied field, so a client cannot forge a role or hijack /
reset another session's accumulated risk mid-conversation.

Format: base64url(json({"sid": ..., "role": ..., "exp": ...})) + "." + hmac_hex
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


def issue_ticket(role: str, session_id: Optional[str] = None, ttl_seconds: int = DEFAULT_TICKET_TTL_SECONDS) -> Tuple[str, str]:
    """
    Create a new signed ticket. session_id is always server-generated for a
    brand-new session; callers never pass a client-supplied id in as the
    identity of a *continuing* session (that's the vulnerability this closes).

    Returns (ticket, session_id).
    """
    sid = session_id or str(uuid.uuid4())
    payload = {"sid": sid, "role": role, "exp": time.time() + ttl_seconds}
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode("utf-8")
    signature = _sign(payload_b64)
    return f"{payload_b64}.{signature}", sid


def verify_ticket(token: str) -> Optional[Tuple[str, str]]:
    """
    Verify a ticket and return (session_id, role) if valid and unexpired.
    Returns None on any failure (missing, malformed, tampered, expired) —
    callers should treat that the same as "no ticket", i.e. start fresh.
    """
    if not token or "." not in token:
        return None

    payload_b64, _, signature = token.partition(".")
    expected_signature = _sign(payload_b64)

    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8"))
        sid = payload["sid"]
        role = payload["role"]
        exp = payload["exp"]
    except (ValueError, KeyError, TypeError):
        return None

    if time.time() > exp:
        return None

    return sid, role
