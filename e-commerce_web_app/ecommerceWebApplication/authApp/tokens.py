from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
import six

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Generating the hash value using user details and timestamp
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)

# Create an instance of the TokenGenerator
generate_token = TokenGenerator()
