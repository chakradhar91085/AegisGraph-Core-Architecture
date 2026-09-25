"""Verifies real JWT checking with a locally generated key (no network)."""
import time
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from starlette.requests import Request

from app.core.config import settings
from app.security import auth

ISSUER = "https://test.clerk.accounts.dev"
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def token(key=KEY, **overrides):
    claims = {"sub": "user_1", "iss": ISSUER, "exp": time.time() + 60, "azp": "http://localhost:5173"}
    claims.update(overrides)
    return jwt.encode({k: v for k, v in claims.items() if v is not None}, key, algorithm="RS256")


def request_with(bearer: str | None) -> Request:
    headers = [(b"authorization", f"Bearer {bearer}".encode())] if bearer else []
    return Request({"type": "http", "headers": headers})


@pytest.fixture(autouse=True)
def _config():
    with patch.object(settings, "CLERK_ISSUER", ISSUER), \
         patch.object(settings, "SECURITY_USER_ROLES", "user_1:Auditor, user_2:Analyst,user_3:Nonsense"), \
         patch.object(auth, "_signing_key", lambda t: KEY.public_key()):
        yield


async def test_valid_token_maps_user_and_role():
    assert await auth.current_user(request_with(token())) == auth.User("user_1", "Auditor")
    assert (await auth.current_user(request_with(token(sub="user_2")))).role == "Analyst"


async def test_unknown_or_invalid_role_mapping_falls_back_to_standard():
    assert (await auth.current_user(request_with(token(sub="user_9")))).role == "Standard"
    assert (await auth.current_user(request_with(token(sub="user_3")))).role == "Standard"


@pytest.mark.parametrize("bad", [
    lambda: None,                                   # no header
    lambda: "garbage",                              # not a JWT
    lambda: token(exp=time.time() - 3600),          # expired
    lambda: token(iss="https://evil.example.com"),  # wrong issuer
    lambda: token(key=OTHER_KEY),                   # signed by someone else
    lambda: token(azp="https://evil.example.com"),  # issued to another app
    lambda: token(sub=None),                        # no subject
])
async def test_bad_tokens_are_rejected(bad):
    with pytest.raises(HTTPException) as e:
        await auth.current_user(request_with(bad()))
    assert e.value.status_code == 401


async def test_unsigned_token_is_rejected():
    forged = jwt.encode({"sub": "user_1", "iss": ISSUER, "exp": time.time() + 60}, key=None, algorithm="none")
    with pytest.raises(HTTPException) as e:
        await auth.current_user(request_with(forged))
    assert e.value.status_code == 401


async def test_only_auditor_is_admin():
    assert (await auth.require_admin(auth.User("a", "Auditor"))).role == "Auditor"
    with pytest.raises(HTTPException) as e:
        await auth.require_admin(auth.User("a", "Analyst"))
    assert e.value.status_code == 403
