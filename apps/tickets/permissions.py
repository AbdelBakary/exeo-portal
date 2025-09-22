"""
Custom permissions for the tickets application.
"""
from rest_framework import permissions


class CanCreateTicket(permissions.BasePermission):
    """
    Custom permission to allow ticket creation.
    """
    
    def has_permission(self, request, view):
        # Admin and SOC analysts can create tickets
        if request.user.role in ['admin', 'soc_analyst']:
            return True
        
        # Client users can create tickets for their organization
        if request.user.role == 'client' and request.user.client:
            return True
        
        return False


class CanViewClientTickets(permissions.BasePermission):
    """
    Custom permission to allow viewing client tickets.
    """
    
    def has_permission(self, request, view):
        # Admin and SOC analysts can view all tickets
        if request.user.role in ['admin', 'soc_analyst']:
            return True
        
        # Client users can view tickets from their organization
        if request.user.role == 'client':
            return True
        
        return False


class CanModifyTicket(permissions.BasePermission):
    """
    Custom permission to allow ticket modification.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin and SOC analysts can modify all tickets
        if request.user.role in ['admin', 'soc_analyst']:
            return True
        
        # Client users can only modify their own tickets if they are open
        if (request.user.role == 'client' and 
            request.user.client == obj.client and 
            request.user == obj.created_by and 
            obj.status in ['open', 'waiting_client']):
            return True
        
        return False


class CanAssignTicket(permissions.BasePermission):
    """
    Custom permission to allow ticket assignment.
    """
    
    def has_permission(self, request, view):
        # Only admin and SOC analysts can assign tickets
        return request.user.role in ['admin', 'soc_analyst']


class CanViewAllTickets(permissions.BasePermission):
    """
    Custom permission to allow viewing all tickets (SOC view).
    """
    
    def has_permission(self, request, view):
        # Only admin and SOC analysts can view all tickets
        return request.user.role in ['admin', 'soc_analyst']


class CanManageTicketTemplates(permissions.BasePermission):
    """
    Custom permission to allow managing ticket templates.
    """
    
    def has_permission(self, request, view):
        # Only admin and SOC analysts can manage templates
        return request.user.role in ['admin', 'soc_analyst']


class CanManageTicketSLA(permissions.BasePermission):
    """
    Custom permission to allow managing ticket SLA.
    """
    
    def has_permission(self, request, view):
        # Only admin can manage SLA
        return request.user.role == 'admin'


class IsTicketOwnerOrSOC(permissions.BasePermission):
    """
    Custom permission to allow access to ticket details.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin and SOC analysts can access all tickets
        if request.user.role in ['admin', 'soc_analyst']:
            return True
        
        # Client users can access tickets from their organization
        if (request.user.role == 'client' and 
            request.user.client and 
            request.user.client == obj.client):
            return True
        
        return False


class CanAddTicketComment(permissions.BasePermission):
    """
    Custom permission to allow adding comments to tickets.
    """
    
    def has_permission(self, request, view):
        # Admin and SOC analysts can add comments to all tickets
        if request.user.role in ['admin', 'soc_analyst']:
            return True
        
        # Client users can add comments to tickets from their organization
        if request.user.role == 'client' and request.user.client:
            return True
        
        return False


class CanUploadTicketAttachment(permissions.BasePermission):
    """
    Custom permission to allow uploading attachments to tickets.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin and SOC analysts can upload attachments to all tickets
        if request.user.role in ['admin', 'soc_analyst']:
            return True
        
        # Client users can upload attachments to tickets from their organization
        if request.user.role == 'client' and request.user.client == obj.client:
            return True
        
        return False
