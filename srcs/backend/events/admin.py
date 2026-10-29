from django.contrib import admin
from .models import Tag, Event, Media


class MediaInline(admin.TabularInline):
    model = Media
    extra = 1          # una riga vuota per caricare subito un file


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag_name')
    search_fields = ('tag_name',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'organizer', 'status', 'event_date')
    list_filter = ('status', 'tags')
    search_fields = ('title', 'organizer__username')
    filter_horizontal = ('tags',)     # selettore a due colonne per i tag
    inlines = [MediaInline]           # aggiungi l'immagine/video dentro l'evento

