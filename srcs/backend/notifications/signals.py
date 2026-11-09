from django.db.models.signals import post_save
from django.dispatch import receiver
from social.models import Follow, Like, Comment  # Verifica che i nomi combacino con il tuo social/models.py
from .services import create_notification

# 1. Sensore per i nuovi Follow
@receiver(post_save, sender=Follow)
def notify_on_follow(sender, instance, created, **kwargs):
    if created:
        create_notification(
            sender=instance.follower,
            recipient=instance.following,
            notification_type='follow'
        )

# 2. Sensore per i nuovi Like
@receiver(post_save, sender=Like)
def notify_on_like(sender, instance, created, **kwargs):
    if created:
        # Assumendo che il modello Like abbia 'user' e 'post' (o 'event')
        create_notification(
            sender=instance.user,
            recipient=instance.post.author,
            notification_type='like',
            target_id=instance.post.id
        )

# 3. Sensore per Commenti e Risposte ai commenti
@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if created:
        # Se il commento ha un genitore (è una risposta a un altro commento)
        if getattr(instance, 'parent_comment', None):
            create_notification(
                sender=instance.author,
                recipient=instance.parent_comment.author,
                notification_type='reply',
                target_id=instance.post.id,
                extra_text=instance.content
            )
        # Altrimenti è un commento normale al post/evento
        else:
            create_notification(
                sender=instance.author,
                recipient=instance.post.author,
                notification_type='comment',
                target_id=instance.post.id,
                extra_text=instance.content
            )
