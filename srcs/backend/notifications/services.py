"""Funzioni per creare/togliere notifiche. Le chiamano le view di social."""
import logging

from .models import Notification

logger = logging.getLogger(__name__)


def short(text, limit=60):
    """Accorcia un testo lungo per metterlo dentro la notifica."""
    text = (text or '').strip().replace('\n', ' ')
    return text if len(text) <= limit else text[:limit - 1] + '…'


def notify(recipient, sender, notification_type, text, event=None, comment=None, unique=False):
    """
    Crea una notifica per `recipient` causata da `sender`.
    - Non notifica mai se stessi.
    - unique=True: per azioni che si possono ripetere (like, follow, reazione) tiene UNA
      sola notifica invece di crearne una nuova ogni volta.
    - Un errore qui non deve mai rompere l'azione principale (like, commento...).
    """
    if recipient is None or recipient.pk == sender.pk:
        return None
    try:
        if unique:
            obj, _ = Notification.objects.update_or_create(
                recipient=recipient, sender=sender, notification_type=notification_type,
                event=event, comment=comment,
                defaults={'notification_txt': text, 'is_read': False},
            )
            return obj
        return Notification.objects.create(
            recipient=recipient, sender=sender, notification_type=notification_type,
            event=event, comment=comment, notification_txt=text,
        )
    except Exception:
        logger.exception('Could not create notification')
        return None


def unnotify(recipient, sender, notification_type, event=None, comment=None):
    """Toglie la notifica quando l'azione viene annullata (unlike, unfollow...)."""
    if recipient is None:
        return
    try:
        Notification.objects.filter(
            recipient=recipient, sender=sender, notification_type=notification_type,
            event=event, comment=comment,
        ).delete()
    except Exception:
        logger.exception('Could not remove notification')
