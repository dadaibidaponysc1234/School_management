from rest_framework import serializers
from user_registration.models import Notification,Teacher, Class

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at', 'is_read']

class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications.
    """
    class Meta:
        model = Notification
        fields = ['title', 'content', 'recipient_user', 'recipient_group', 'notification_type']

class NotificationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating notifications.
    """
    class Meta:
        model = Notification
        fields = ['title', 'content', 'is_read']



