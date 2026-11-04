from django.db import models
from django.conf import settings


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('like', 'Like'),                  # like a un evento
        ('comment', 'Comment'),            # commento a un evento
        ('reply', 'Reply'),                # risposta a un commento
        ('reaction', 'Reaction'),          # reazione (like, risata...) a un commento
        ('subscription', 'Subscription'),  # qualcuno ha iniziato a seguirti
        ('registration', 'Registration'),
        ('system', 'System'),
    ]

    # chi RICEVE la notifica
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_notifications')
    # chi ha COMPIUTO l'azione
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    # commento collegato (il nuovo commento/risposta, o il commento che ha ricevuto la reazione)
    comment = models.ForeignKey('social.Comment', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    # Testo SENZA il nome di chi agisce (es. "started following you"): il nome lo
    # aggiunge il frontend leggendolo dall'utente, cosi' non resta vecchio se cambia username.
    notification_txt = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
