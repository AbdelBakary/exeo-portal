"""
Custom authentication classes for the accounts application.
"""
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Custom JWT authentication class.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using JWT token.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
        
        try:
            # Extract token from "Bearer <token>" format
            token = auth_header.split(' ')[1]
        except IndexError:
            return None
        
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Get user from payload
            user_id = payload.get('user_id')
            if not user_id:
                return None
            
            user = User.objects.get(id=user_id)
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
    
    def authenticate_header(self, request):
        """
        Return the authentication header.
        """
        return 'Bearer'
