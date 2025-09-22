"""
Serializers for the accounts application.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Client, UserSession, AuditLog


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model."""
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'contact_email', 'contact_phone', 'address',
            'created_at', 'updated_at', 'is_active', 'timezone',
            'notification_preferences', 'custom_settings'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'client', 'client_name', 'phone', 'avatar', 'mfa_enrolled',
            'is_verified', 'created_at', 'updated_at', 'preferences',
            'notification_settings'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'mfa_enrolled']
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if self.instance and self.instance.email == value:
            return value
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password',
            'password_confirm', 'role', 'client', 'phone'
        ]
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
    
    def create(self, validated_data):
        """Create new user."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'avatar', 'preferences',
            'notification_settings'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Ancien mot de passe incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return attrs


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        """Validate login credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Email ou mot de passe incorrect.")
            if not user.is_active:
                raise serializers.ValidationError("Ce compte est désactivé.")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Email et mot de passe requis.")
        
        return attrs


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for UserSession model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'user_email', 'ip_address', 'user_agent',
            'created_at', 'last_activity', 'is_active'
        ]
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'action', 'resource_type',
            'resource_id', 'description', 'ip_address', 'user_agent',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
