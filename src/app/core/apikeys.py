from secrets import token_urlsafe
import hashlib
from pwdlib import PasswordHash

hasher = PasswordHash.recommended()

def generate_api_key():
    secret = token_urlsafe(32)
    prefix = "tf_"
    api_key = f"{prefix}{secret}"
    return api_key, prefix   


def create_api_key_hashes(api_key: str):
    lookup_hash = hashlib.sha256(api_key.encode()).hexdigest()
    verify_hash = hasher.hash(api_key)
    return lookup_hash, verify_hash


def verify_api_key(api_key: str, hash: str):
    return hasher.verify(api_key, hash)