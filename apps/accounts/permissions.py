"""
Custom permissions for the accounts application.
"""
from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins to access objects.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the object."""
        # Admin users have full access
        if request.user.role == 'admin':
            return True
        
        # SOC analysts have full access
        if request.user.role == 'soc_analyst':
            return True
        
        # Users can only access their own data
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'id'):
            return obj.id == request.user.id
        
        return False


class IsClientOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow client owners or admins to access objects.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the object."""
        # Admin users have full access
        if request.user.role == 'admin':
            return True
        
        # SOC analysts have full access
        if request.user.role == 'soc_analyst':
            return True
        
        # Client users can only access their client's data
        if request.user.role == 'client':
            if hasattr(obj, 'client'):
                return obj.client == request.user.client
            elif hasattr(obj, 'user') and hasattr(obj.user, 'client'):
                return obj.user.client == request.user.client
        
        return False


class IsAdminOrSOCAnalyst(permissions.BasePermission):
    """
    Custom permission to only allow admins or SOC analysts.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission."""
        return request.user.role in ['admin', 'soc_analyst']


class IsAdminOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission."""
        return request.user.role == 'admin'


class CanAccessClientData(permissions.BasePermission):
    """
    Custom permission to check if user can access client data.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access client data."""
        # Admin and SOC analysts can access all client data
        if request.user.role in ['admin', 'soc_analyst']:
            return True
        
        # Client users can only access their own client's data
        if request.user.role == 'client':
            client_id = request.data.get('client_id') or request.query_params.get('client_id')
            if client_id:
                return str(request.user.client_id) == str(client_id)
            return True
        
        return False


class IsClientOwner(permissions.BasePermission):
    """
    Custom permission to only allow client owners to access their data.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the object."""
        # Admin and SOC analysts have full access
        if request.user.role in ['admin', 'soc_analyst']:
            return True
        
        # Client users can only access their client's data
        if request.user.role == 'client':
            if hasattr(obj, 'client'):
                return obj.client == request.user.client
            elif hasattr(obj, 'user') and hasattr(obj.user, 'client'):
                return obj.user.client == request.user.client
        
        return False


class IsAdminOrAnalyst(permissions.BasePermission):
    """
    Custom permission to only allow admins or SOC analysts.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission."""
        return request.user.role in ['admin', 'soc_analyst']
