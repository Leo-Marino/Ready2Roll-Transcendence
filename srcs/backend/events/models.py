from django.db import models
from django.conf import settings

class Tag(models.Model):
    tag_name = models.CharField(max_length=55, unique=True)
    def __str__(self):
        return self.tag_name
    class Meta:
        db_table = 'tags'

class Event(models.Model):
    def __str__(self):
        return self.title
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
    ]

    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description= models.TextField()
    location = models.TextField(blank=True, null=True)
    event_date = models.DateTimeField()
    max_capacity = models.IntegerField(blank=True, null=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='events', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Draft')

    class Meta:
        db_table = 'events'

class Media(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='media')
    media_url =  models.FileField(upload_to='event_media/', null=True, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'media'
