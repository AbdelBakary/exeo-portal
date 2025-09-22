"""
Models for the accounts application.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class Client(models.Model):
    """Model representing a client organization."""
    
    name = models.CharField(max_length=200, unique=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Configuration parameters
    timezone = models.CharField(max_length=50, default='Europe/Paris')
    notification_preferences = models.JSONField(default=dict, blank=True)
    custom_settings = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser."""
    
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('soc_analyst', 'Analyste SOC'),
        ('client', 'Client'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    mfa_enrolled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User preferences
    preferences = models.JSONField(default=dict, blank=True)
    notification_settings = models.JSONField(default=dict, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def can_access_client_data(self, client_id):
        """Check if user can access data for a specific client."""
        if self.role == 'admin':
            return True
        if self.role == 'soc_analyst':
            return True
        if self.role == 'client' and self.client_id == client_id:
            return True
        return False


class UserSession(models.Model):
    """Model to track user sessions for security purposes."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_activity']
        verbose_name = 'Session utilisateur'
        verbose_name_plural = 'Sessions utilisateur'
    
    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"


class AuditLog(models.Model):
    """Model to track user actions for audit purposes."""
    
    ACTION_CHOICES = [
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
        ('view', 'Consultation'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50)  # e.g., 'Alert', 'Incident'
    resource_id = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Log d\'audit'
        verbose_name_plural = 'Logs d\'audit'
    
    def __str__(self):
        return f"{self.user.email if self.user else 'System'} - {self.action} - {self.resource_type}"
