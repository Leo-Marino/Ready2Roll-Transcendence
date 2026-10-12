from rest_framework import serializers
from django.contrib.auth import get_user_model

<<<<<<< HEAD:srcs/backend/test/serializers.py
=======


>>>>>>> backend:srcs/backend/users/serializers.py
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
<<<<<<< HEAD:srcs/backend/test/serializers.py
        fields = ['username', 'email', 'password', 'type_of_user', 'legal_name', 'vat_tax']
=======
        fields = ['username', 'email', 'password']
>>>>>>> backend:srcs/backend/users/serializers.py
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Used to READ the logged-in user's profile (GET /api/profile/)."""
    following_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'bio',
            'avatar_url', 'instagram_handle', 'bs_website',
            'following_count', 'followers_count', 'type_of_user'
        ]

    # Placeholders until you build a follow system
    def get_following_count(self, obj):
        return 0

    def get_followers_count(self, obj):
        return 0

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'bio',
            'avatar_url',
            'instagram_handle',
            'phone_number',
            'legal_name',
            'date_of_birth',
            'bs_website'
        ]
