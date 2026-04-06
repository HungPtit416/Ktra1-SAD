from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed as DRFAuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication for microservices.
    Automatically creates users based on JWT payload if they don't exist.
    """

    def authenticate(self, request):
        try:
            # Try parent authentication first
            result = super().authenticate(request)
            if result is None:
                return None
            return result
        except (InvalidToken, DRFAuthenticationFailed) as e:
            # If parent auth fails, check if it's User.DoesNotExist
            if 'User not found' in str(e) or 'not found' in str(e).lower():
                # Manually extract token from Authorization header
                try:
                    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
                    if not auth_header or not auth_header.startswith('Bearer '):
                        return None
                    
                    raw_token = auth_header[7:]  # Remove 'Bearer '
                    validated_token = self.get_validated_token(raw_token)
                    
                    # Create user from token payload
                    user_id = validated_token.get('user_id')
                    if not user_id:
                        raise DRFAuthenticationFailed('Invalid token: no user_id')
                    
                    user, created = User.objects.get_or_create(
                        id=user_id,
                        defaults={'username': f'user_{user_id}'}
                    )
                    return (user, validated_token)
                except InvalidToken as inv_e:
                    raise DRFAuthenticationFailed(str(inv_e))
                except Exception as inner_e:
                    raise DRFAuthenticationFailed(f'Auth error: {str(inner_e)}')
            raise
