from rest_framework import serializers
from django.db.models import Count
from .models import Comment

DEFAULT_AVATAR = "https://i.pravatar.cc/150?u=6"


# extract data and post comment
class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()
    user_reaction = serializers.SeralizerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'created_at', 'parent_comment',
            'user_username', 'user_avatar', 'reply_count', 'replies',
            'reaction_count', 'user_reaction',
        ]

    def get_user_avatar(self, obj):
        if obj.user.avatar_url:
            avatar_str = str(obj.user.avatar_url)
            if avatar_str.startswith('http'):
                return avatar_str
            return obj.user.avatar_url.url
        return DEFAULT_AVATAR

    def get_replies(self, obj):
        # Only top-level comments carry replies (Instagram style: one level deep)
        if obj.parent_comment_id is not None:
            return []
        replies = obj.replies.select_related('user').order_by('created_at')
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_reply_count(self, obj):
        if obj.parent_comment_id is not None:
            return 0
        return obj.replies.count()

    def get_reaction_count(self, obj):
        counts = obj.reactions.values('reaction_type').annotate(count=Count('id'))
        return {item['reaction_type']: item['count'] for item in counts}

    def get_user_reaction(self, obj):
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                reaction = obj.reactions.filter(user=request.user).first()
                return reaction.reaction_type if reaction else None
            return None
