import hashlib
import hmac
import base64
import json
from datetime import datetime, timedelta

SECRET_KEY = "hookwatch_super_secret_hackathon_key"

def hash_password(password: str) -> str:
    # Basic SHA256 hashing without external dependencies like bcrypt (perfect for hackathon constraints)
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(user_id: str) -> str:
    # A standalone JWT implementation using standard libraries (no pyjwt required)
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "exp": (datetime.utcnow() + timedelta(days=7)).timestamp()
    }
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signature = hmac.new(
        SECRET_KEY.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256
    ).digest()
    
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def get_user_id_from_token(token: str) -> str:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
            
        header, payload_b64, signature = parts
        
        # Pad payload to be valid base64
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        
        if payload.get("exp", 0) < datetime.utcnow().timestamp():
            return None # Expired
            
        return payload.get("sub")
    except Exception:
        return None
