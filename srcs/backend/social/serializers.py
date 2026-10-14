from rest_framework import serializers
from .models import Comment
from django.contrib.auth import get_user_model

#extract data and post comment
class CommentSerializer(serializers.ModelSerializer):
	user_name = serializers.CharField(source='user.username', read_only=True)
	user_avatar = serializers.SerializerMethodField()

	class Meta:
		model = Comment
		fields = ['id', 'content', 'created_at', 'user_username', 'user_avatar']

	def get_user_avatar(self, obj):

		if obj.user.avatar_url:
			avatar_str = str(obj.user.avatar_url)
			if avatar_str.startswith('http'):
				return avatar_str
			return f"http://localhost:9000/media/{avatar_str}"
		return "https://i.pravatar.cc/150?u=6"
