from rest_framework import serializers
from .models import Event, Media, Tag
from social.serializers import DEFAULT_AVATAR

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "tag_name"]

class TagNameField(serializers.SlugRelatedField):
    """
    Accetta i tag come NOMI (es. "party", "techno") invece che come id.
    Se un tag non esiste ancora lo crea al volo.
    In lettura restituisce il nome del tag.
    """
    def to_internal_value(self, data):
        name = str(data).strip().lower()
        if not name:
            raise serializers.ValidationError("Il tag non può essere vuoto.")
        if len(name) > 55:
            raise serializers.ValidationError("Il tag può avere al massimo 55 caratteri.")
        tag, _ = self.get_queryset().get_or_create(tag_name=name)
        return tag

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ["id", "media_url", "media_type", "created_at"]

class EventSerializer(serializers.ModelSerializer):
    media_file = serializers.FileField(write_only=True, required=False)
    media_src = serializers.SerializerMethodField()
    media_type = serializers.SerializerMethodField()
    tags = TagNameField(
    many=True,
    slug_field='tag_name',
    queryset=Tag.objects.all(),
    required=False,
    )
    # statistics shown in the owner's profile
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id", "title", "organizer", "description",
            "location", "event_date", "max_capacity",
            "ticket_price", "end_time", "start_time","tags", "created_at",
            "status", "media_file", "media_type", "media_src",
            "likes_count", "comments_count",
        ]
        read_only_fields = ['organizer']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        # comments + replies, same number the home feed shows
        return obj.comments.count()

    def get_media_src(self, obj):
        media = Media.objects.filter(event=obj).first()
        if media and media.media_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(media.media_url.url)
            return media.media_url.url
        return None

    def get_media_type(self, obj):
        media = Media.objects.filter(event=obj).first()
        return media.media_type if media else None

    def get_media_src(self, obj):
            media = Media.objects.filter(event=obj).first()
            if media and media.media_url:
                # Force a relative path so the frontend uses the current domain/port (e.g. localhost:8080)
                return f"/media/{media.media_url.name}"
            return None

    def get_media_type(self, obj):
        media = Media.objects.filter(event=obj).first()
        return media.media_type if media else None

    def create(self, validated_data):
        media_file = validated_data.pop('media_file', None)

        request = self.context.get('request')
        m_type = request.data.get('media_type', 'image') if request else 'image'

        event = super().create(validated_data)

        if media_file:
            Media.objects.create(
                event=event,
                media_url=media_file,
                media_type=m_type
            )

        return event




class FeedEventSerializer(serializers.ModelSerializer):
    """One video of the home feed: media + owner info + stats."""
    media_src = serializers.SerializerMethodField()
    media_type = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id", "title", "description", "created_at", "event_date", "location",
            "media_src", "media_type",
            "likes_count", "comments_count", "is_liked", "owner", "tags",
        ]

    def _media(self, obj):
        return obj.media.all().first()

    def _viewer(self):
        request = self.context.get('request')
        return request.user if request and request.user.is_authenticated else None

    def get_media_src(self, obj):
        media = self._media(obj)
        if media and media.media_url:
            request = self.context.get('request')
            url = media.media_url.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_media_src(self, obj):
        media = self._media(obj)
        if media and media.media_url:
            return f"/media/{media.media_url.name}"
        return None

    def get_media_type(self, obj):
        media = self._media(obj)
        return media.media_type if media else None

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_tags(self, obj):
        return [tag.tag_name for tag in obj.tags.all()]

    def get_is_liked(self, obj):
        viewer = self._viewer()
        return bool(viewer) and obj.likes.filter(user=viewer).exists()

    def get_owner(self, obj):
        user = obj.organizer
        viewer = self._viewer()
        avatar = DEFAULT_AVATAR
        if user.avatar_url:
            avatar = str(user.avatar_url) if str(user.avatar_url).startswith('http') else user.avatar_url.url
        return {
            "id": user.id,
            "username": user.username,
            "display_name": user.legal_name or user.username,
            "avatar": avatar,
            "is_self": bool(viewer) and viewer.pk == user.pk,
            "is_following": bool(viewer) and viewer.pk != user.pk
                            and user.followers.filter(follower=viewer).exists(),
        }
