from rest_framework import serializers
from collections import Counter
from .models import Comment

DEFAULT_AVATAR = "https://i.pravatar.cc/150?u=6"


# extract data and post comment
class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'created_at', 'parent_comment',
            'user_username', 'user_avatar', 'reply_count', 'replies',
            'reactions_count', 'user_reaction',
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
        replies = sorted(obj.replies.all(), key=lambda r: r.created_at)
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_reply_count(self, obj):
        if obj.parent_comment_id is not None:
            return 0
        return len(obj.replies.all())

    def get_reactions_count(self, obj):
        return dict(Counter(r.reaction_type for r in obj.reactions.all()))

    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        for reaction in obj.reactions.all():
            if reaction.user_id == request.user.id:
                return reaction.reaction_type
        return None


