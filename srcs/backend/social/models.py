from django.db import models
from django.conf import settings

class Subscription(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscriptions'
        constraints = [
            models.UniqueConstraint(fields=['follower', 'followed'], name='unique_subscription')
        ]


class Comment(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    ]

    content = models.TextField(blank=False, null=False)
    type_content = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='text')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'

class EventLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_likes')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_likes'
        constraints = [
            models.UniqueConstraint(fields=['user', 'event'], name='unique_user_event_like')
        ]


class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', '❤️'),
        ('laugh', '😂'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😡'),
        ('thumbs_up', '👍'),
        ('thumbs_down', '👎'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reactions')
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='reactions', null=True, blank=True)
    direct_message = models.ForeignKey('DirectMessage', on_delete=models.CASCADE, related_name='reactions', null=True, blank=True)
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES, default='like')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reactions'
        constraints = [
            models.UniqueConstraint(fields=['user', 'comment'], condition=Q(comment__isnull=False), name='unique_user_comment_reaction'),
            models.UniqueConstraint(fields=['user', 'direct_message'], condition=Q(direct_message__isnull=False), name='unique_user_dm_reaction'),
            models.CheckConstraint(check=(Q(comment__isnull=False, direct_message__isnull=True) | Q(comment__isnull=True, direct_message__isnull=False)),
                name='reaction_either_comment_or_dm'
            )
        ]

class DirectMessage(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    ]

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, null=True, blank=True, related_name='shared_in_messages')
    message_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='text')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_request = models.BooleanField(default=True)

    class Meta:
        db_table = 'direct_messages'
