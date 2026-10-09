from rest_framework import serializers
from .models import Event, Media, Tag


class TagSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tag
		fields = ["id","tag_name"]

class MediaSerializer(serializers.ModelSerializer):
	class Meta:
		model = Media
		fields = ["id", "media_url", "media_type", "created_at"]

class EventSerializer(serializers.ModelSerializer):
	class Meta:
		model = Event
		fields = [
			"id","title", "organizer", "description",
			"location", "event_date", "max_capacity",
			"ticket_price", "end_time", "tags", "created_at"
		]
