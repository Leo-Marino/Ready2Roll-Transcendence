from rest_framework import serializers
from django.contrib.auth import get_user_model
from events.models import Tag

User = get_user_model()

ALLOWED_TAGS = ['Disco', 'Trap', 'Hip Hop', 'Rock', 'Jazz']

class UserSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.ChoiceField(choices=ALLOWED_TAGS), required=False
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'type_of_user', 'legal_name', 'tags','vat_tax']
        extra_kwargs = {'password': {'write_only': True}}
    def validate(selfs,attrs):
        if attrs.get('type_of_user') == 'business':
            errors = {}
            if not (attrs.get('legal_name') or '').strip():
                errors['legal_name'] = 'Business / Venue name is required.'
            if errors:
                    raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        tag_names = validated_data.pop('tags', [])
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            type_of_user=validated_data.get('type_of_user', 'standard'),
            legal_name=validated_data.get('legal_name'),
            vat_tax=validated_data.get('vat_tax'),
        )
        tags = [Tag.objects.get_or_create(tag_name=n)[0] for n in tag_names]
        user.tags.set(tags)
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

             'id', 'username', 'email', 'first_name', 'last_name', 'bio',
            'avatar_url', 'instagram_handle', 'bs_website',
            'following_count', 'followers_count', 'type_of_user',
        ]

class ViewerRelationMixin(serializers.Serializer):
    is_following = serializers.SerializerMethodField()
    is_self = serializers.SerializerMethodField()

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

class AvatarUrlMixin(serializers.Serializer):
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        if obj.avatar_url and obj.avatar_url.name:
            # Force a relative path so the frontend uses the correct domain/port
            return f"/media/{obj.avatar_url.name}"
        return None

class PublicUserProfileSerializer(FollowCountsMixin, ViewerRelationMixin, AvatarUrlMixin, serializers.ModelSerializer):
    """Profilo visto da un ALTRO utente (GET /api/users/<id>/). Niente dati privati."""

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'bio',
            'avatar_url', 'instagram_handle', 'bs_website',
            'following_count', 'followers_count',
            'is_following', 'is_self', 'type_of_user',
        ]

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
            'bs_website',
        ]

class FollowUserSerializer(ViewerRelationMixin, serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'username', 'avatar_url', 'is_following', 'is_self',
        ]
