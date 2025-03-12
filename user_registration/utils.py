import hmac
import hashlib
import base64
from django.conf import settings

def generate_temp_token(pin_id, otp):
    """
    Generate a secure temp_token using HMAC and base64 encoding.
    """
    message = f"{pin_id}-{otp}".encode('utf-8')
    secret_key = settings.SECRET_KEY.encode('utf-8')
    signature = hmac.new(secret_key, message, hashlib.sha256).digest()
    token = f"{pin_id}:{base64.urlsafe_b64encode(signature).decode('utf-8')}"
    return token

def validate_temp_token(temp_token):
    """
    Validate the temp_token by recalculating its HMAC signature.
    """
    try:
        pin_id, encoded_signature = temp_token.split(':')
        from .models import StudentRegistrationPin  # Import here to avoid circular imports
        pin = StudentRegistrationPin.objects.get(pin_id=pin_id, is_used=False)
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            f"{pin_id}-{pin.otp}".encode('utf-8'),
            hashlib.sha256
        ).digest()
        is_valid = hmac.compare_digest(
            base64.urlsafe_b64encode(expected_signature).decode('utf-8'),
            encoded_signature
        )
        return is_valid, pin
    except (ValueError, StudentRegistrationPin.DoesNotExist):
        return False, None
