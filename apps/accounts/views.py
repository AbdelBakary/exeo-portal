"""
Views for the accounts application.
"""
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import User, Client, UserSession, AuditLog
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, LoginSerializer, UserSessionSerializer,
    AuditLogSerializer, ClientSerializer
)
from .permissions import IsOwnerOrAdmin, IsClientOwnerOrAdmin


class LoginView(APIView):
    """View for user login."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle user login."""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Create JWT token
            payload = {
                'user_id': user.id,
                'email': user.email,
                'role': user.role,
                'client_id': user.client_id,
                'exp': datetime.utcnow() + timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
            
            # Create user session
            UserSession.objects.create(
                user=user,
                session_key=token,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Log login event
            AuditLog.objects.create(
                user=user,
                action='login',
                resource_type='User',
                resource_id=str(user.id),
                description=f'User {user.email} logged in',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'token': token,
                'user': UserSerializer(user).data,
                'expires_in': settings.JWT_ACCESS_TOKEN_LIFETIME
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """View for user logout."""
    
    def post(self, request):
        """Handle user logout."""
        # Deactivate current session
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
                UserSession.objects.filter(session_key=token).update(is_active=False)
            except IndexError:
                pass
        
        # Log logout event
        AuditLog.objects.create(
            user=request.user,
            action='logout',
            resource_type='User',
            resource_id=str(request.user.id),
            description=f'User {request.user.email} logged out',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': 'Logged out successfully'})


class UserProfileView(APIView):
    """View for user profile management."""
    
    def get(self, request):
        """Get current user profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update current user profile."""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Log profile update
            AuditLog.objects.create(
                user=request.user,
                action='update',
                resource_type='User',
                resource_id=str(request.user.id),
                description=f'User {request.user.email} updated profile',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """View for password change."""
    
    def post(self, request):
        """Handle password change."""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Log password change
            AuditLog.objects.create(
                user=user,
                action='update',
                resource_type='User',
                resource_id=str(user.id),
                description=f'User {user.email} changed password',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListCreateView(generics.ListCreateAPIView):
    """View for listing and creating users."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'client', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email', 'last_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter users based on user role and client."""
        queryset = super().get_queryset()
        
        # If user is a client, only show users from their client
        if self.request.user.role == 'client':
            queryset = queryset.filter(client=self.request.user.client)
        
        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for user detail operations."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class ClientListCreateView(generics.ListCreateAPIView):
    """View for listing and creating clients."""
    
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'contact_email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for client detail operations."""
    
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class UserSessionListView(generics.ListAPIView):
    """View for listing user sessions."""
    
    serializer_class = UserSessionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['created_at', 'last_activity']
    ordering = ['-last_activity']
    
    def get_queryset(self):
        """Filter sessions based on user role."""
        queryset = UserSession.objects.all()
        
        # If user is a client, only show their sessions
        if self.request.user.role == 'client':
            queryset = queryset.filter(user=self.request.user)
        
        return queryset


class AuditLogListView(generics.ListAPIView):
    """View for listing audit logs."""
    
    serializer_class = AuditLogSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['action', 'resource_type', 'user']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter audit logs based on user role."""
        queryset = AuditLog.objects.all()
        
        # If user is a client, only show logs related to their client
        if self.request.user.role == 'client':
            queryset = queryset.filter(user__client=self.request.user.client)
        
        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def refresh_token(request):
    """Refresh JWT token."""
    try:
        # Create new token with updated expiration
        payload = {
            'user_id': request.user.id,
            'email': request.user.email,
            'role': request.user.role,
            'client_id': request.user.client_id,
            'exp': datetime.utcnow() + timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        return Response({
            'token': token,
            'expires_in': settings.JWT_ACCESS_TOKEN_LIFETIME
        })
    except Exception as e:
        return Response(
            {'error': 'Token refresh failed'},
            status=status.HTTP_400_BAD_REQUEST
        )
