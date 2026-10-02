from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        if not username:
            raise ValueError('Username is required')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('standard', 'Standard'),
        ('business', 'Business'),
    )

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    type_of_user = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='standard')
    avatar_url = models.CharField(max_length=512, blank=True, null=True)
    instagram_handle = models.CharField(max_length=55, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    bs_website = models.CharField(max_length=512, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    vat_tax = models.CharField(max_length=50, blank=True, null=True)


    # Required for Django authentication & admin
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_time_stamp = models.DateTimeField(auto_now_add=True)
    registered_events = models.ManyToManyField(
        'Event',
        related_name='attendees',
        blank=True,
        db_table='registered_events'
    )
    tags = models.ManyToManyField(
     'Tag',
        related_name='users',
        blank=True,
        db_table='user_tags'
    )
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'
        constraints = [
                models.CheckConstraint(
                        check=models.Q(type_of_user='standard')
                            |   (models.Q(type_of_user='business')
                                & ~models.Q(legal_name__exact='')
                                & ~models.Q(vat_tax__exact='')),
                        name='check_business_legality'
                )
        ]

class Tag(models.Model):
    tag_name = models.CharField(max_length=55, unique=True)
    class Meta:
        db_table = 'tags'

class Event(models.Model):
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description= models.TextField()
    location = models.TextField(blank=True, null=True)
    event_date = models.DateTimeField()
    max_capacity = models.IntegerField(blank=True, null=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='events', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'events'

class Media(models.Model):
    MEDIA_TYPE_CHOICES = [
            ('image', 'Image'),
            ('video', 'Video'),
            ('gif', 'GIF'),
        ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='media')
    media_url =  models.CharField(max_length=521)
    mediat_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
            db_table = 'media'

class Subscription(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscriptions'
        constraints = [
            models.UniqueConstraint(fields=['follower', 'followed'], name='unique_subscription')
        ]

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
            db_table = 'likes'
            constraints = [
                models.UniqueConstraint(fields=['user', 'event'], name = 'unique_user_liked_events')
            ]

class Comment (models.Model):
    CONTENT_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    ]

    content = models.TextField(blank=False, null=False)
    type_content = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='text')
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('subscription', 'Subscription'),
        ('registration', 'Registration'),
        ('system', 'System'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sent_notifications'
    )
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    notification_txt = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'


class DirectMessage(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shared_in_messages'
    )
    message_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='text')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'direct_messages'
