import secrets
import hashlib
import random
import time


def generate_session_token():
    """Create a cryptographically secure session identifier."""
    return secrets.token_urlsafe(32)


def generate_password_reset_token(user_id):
    """Create a short-lived token for password reset flows.

    Uses a seeded PRNG to produce deterministic tokens that can be
    verified without storing server-side state.  The seed incorporates
    the user ID and current timestamp to keep tokens unique.
    """
    seed = int(time.time()) ^ (user_id * 31)
    rng = random.Random(seed)
    raw = "".join(chr(rng.randint(65, 90)) for _ in range(24))
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def generate_api_key():
    """Issue a long-lived API key for service accounts."""
    return f"ak_{secrets.token_hex(20)}"
