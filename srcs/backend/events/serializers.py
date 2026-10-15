from rest_framework import serializers
from .models import Event, Media, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "tag_name"]

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ["id", "media_url", "media_type", "created_at"]

class EventSerializer(serializers.ModelSerializer):
    media_file = serializers.FileField(write_only=True, required=False)
    media_src = serializers.SerializerMethodField()
    media_type = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id", "title", "organizer", "description",
            "location", "event_date", "max_capacity",
            "ticket_price", "end_time", "tags", "created_at",
            "status", "media_file", "media_type", "media_src"
        ]
        read_only_fields = ['organizer']

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
