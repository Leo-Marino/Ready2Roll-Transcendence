import json
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
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            type_of_user=validated_data.get('type_of_user', 'standard'),
            legal_name=validated_data.get('legal_name'),
            vat_tax=validated_data.get('vat_tax'),
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

             'id', 'username', 'email', 'first_name', 'last_name', 'bio',
            'avatar_url', 'instagram_handle', 'bs_website',
            'following_count', 'followers_count', 'type_of_user', 'tags',
        ]
    def get_tags(self, obj):
        return [tag.tag_name for tag in obj.tags.all()]

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
    tags = serializers.CharField(required=False, allow_blank=True)
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
            'tags',
        ]

    def update(self, instance, validated_data):
        raw_tags = validated_data.pop('tags', None)
        user = super().update(instance, validated_data)

        if raw_tags is not None:
            # Strip out any leftover brackets or quotes just in case, then split by comma
            clean_string = raw_tags.replace('[', '').replace(']', '').replace('"', '')
            tag_names = [t.strip() for t in clean_string.split(',') if t.strip()]

            # Blindly create whatever tags were sent and save the relation
            tags_objs = [Tag.objects.get_or_create(tag_name=n)[0] for n in tag_names]
            user.tags.set(tags_objs)

        return user

class FollowUserSerializer(ViewerRelationMixin, AvatarUrlMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'avatar_url', 'is_following', 'is_self',
        ]
