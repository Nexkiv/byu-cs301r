"""Utility for encrypting / decrypting note content at rest.

Uses AES encryption so that sensitive notes aren't stored in plaintext
in the database.  The encryption key is derived from the app's SECRET_KEY
for simplicity.
"""

import base64
import hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from config import SECRET_KEY

# Derive a fixed 256-bit key from SECRET_KEY
_KEY = hashlib.sha256(SECRET_KEY.encode()).digest()


def encrypt_note(plaintext: str) -> str:
    """Encrypt a note's content and return a base64-encoded ciphertext."""
    padded = plaintext.encode().ljust((len(plaintext) // 16 + 1) * 16, b"\x00")
    cipher = Cipher(algorithms.AES(_KEY), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(ct).decode()


def decrypt_note(ciphertext_b64: str) -> str:
    """Decrypt a base64-encoded ciphertext back to plaintext."""
    ct = base64.b64decode(ciphertext_b64)
    cipher = Cipher(algorithms.AES(_KEY), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()
    return padded.rstrip(b"\x00").decode()
