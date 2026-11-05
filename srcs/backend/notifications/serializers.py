from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'sender_username', 'sender_avatar',
            'notification_type', 'target_id', 'message',
            'is_read', 'created_at'
        ]

    def get_sender_avatar(self, obj):
        if getattr(obj.sender, 'avatar_url', None):
            return str(obj.sender.avatar_url)
        return None
