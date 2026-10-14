from rest_framework import serializers
from django.contrib.auth import get_user_model



User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class FollowCountsMixin(serializers.Serializer):
    """Conteggi reali basati sul modello social.Subscription.
    related_name='following' -> le Subscription dove obj e' il follower
    related_name='followers' -> le Subscription dove obj e' il followed
    """
    following_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_followers_count(self, obj):
        return obj.followers.count()


class UserProfileSerializer(FollowCountsMixin, serializers.ModelSerializer):
    """Used to READ the logged-in user's profile (GET /api/profile/)."""
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'bio',
            'avatar_url', 'instagram_handle', 'bs_website',
            'following_count', 'followers_count',
        ]


class PublicUserProfileSerializer(FollowCountsMixin, serializers.ModelSerializer):
    """Profilo visto da un ALTRO utente (GET /api/users/<id>/). Niente dati privati."""
    is_following = serializers.SerializerMethodField()
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'bio',
            'avatar_url', 'instagram_handle', 'bs_website',
            'following_count', 'followers_count',
            'is_following', 'is_self',
        ]

    def _viewer(self):
        request = self.context.get('request')
        return request.user if request and request.user.is_authenticated else None

    def get_is_following(self, obj):
        viewer = self._viewer()
        if viewer is None or viewer.pk == obj.pk:
            return False
        return obj.followers.filter(follower=viewer).exists()

    def get_is_self(self, obj):
        viewer = self._viewer()
        return viewer is not None and viewer.pk == obj.pk


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    avatar_url = serializers.ImageField(required=False, allow_null=True)
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
