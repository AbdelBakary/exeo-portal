"""
Custom middleware for the accounts application.
"""
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate users using JWT tokens.
    """
    
    def process_request(self, request):
        """
        Process the request and set user from JWT token.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return
        
        try:
            # Extract token from "Bearer <token>" format
            token = auth_header.split(' ')[1]
        except IndexError:
            return
        
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
                return
            
            user = User.objects.get(id=user_id)
            request.user = user
            
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            # Token is invalid or user doesn't exist
            pass
