import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

def get_unique_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    # e.g., returns "avatars/123e4567-e89b-12d3.jpg"
    return f"avatars/{uuid.uuid4()}.{ext}"

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
    avatar_url = models.ImageField(upload_to=get_unique_avatar_path, null=True, blank=True)
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

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_time_stamp = models.DateTimeField(auto_now_add=True)

    # Updated to point to the events app
    registered_events = models.ManyToManyField(
        'events.Event',
        related_name='attendees',
        blank=True,
        db_table='registered_events'
    )
    # Updated to point to the events app
    tags = models.ManyToManyField(
        'events.Tag',
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
                check=models.Q(type_of_user='standard') | (models.Q(type_of_user='business') & ~models.Q(legal_name__exact='') & ~models.Q(vat_tax__exact='')),
                name='check_business_legality'
            )
        ]
