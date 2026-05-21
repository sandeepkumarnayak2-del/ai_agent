import re

def sanitize_input(text: str) -> str:
    """Remove dangerous characters"""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip()
    return text

def validate_username(username: str) -> bool:
    """Check username is safe"""
    return bool(re.match(r'^[\w]{2,20}$', username))

def validate_message(message: str) -> tuple[bool, str]:
    """Validate message"""
    if not message or not message.strip():
        return False, "Message cannot be empty"
    if len(message) > 1000:
        return False, "Message too long"
    return True, "ok"