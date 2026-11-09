"""Helpers to push real-time updates to connected WebSocket clients.

Two kinds of groups exist:
- GLOBAL_GROUP: every connected user joins it. Used for public counters
  (likes, comments, reactions, followers) that anybody looking at the same
  content must see change live.
- user_<id>: one private group per user. Used for things that concern only
  that user (e.g. "you have a new notification").
"""
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

logger = logging.getLogger(__name__)

GLOBAL_GROUP = "global_social"


def user_group(user_id):
    return f"user_{user_id}"


def _group_send(group, payload):
    """Send a payload to a channel group. Never raises: a Redis hiccup must
    not break the main action (like, comment, follow...)."""
    layer = get_channel_layer()
    if layer is None:
        return
    try:
        async_to_sync(layer.group_send)(group, payload)
    except Exception:
        logger.exception("Could not broadcast to group %s", group)


def broadcast_social_action(action, target_id, data=None):
    """Tell every connected client that something changed.

    action:    "like" | "comment" | "comment_reaction" | "follow" | "update_profile"
    target_id: id of the object the action refers to (event, comment, user)
    data:      small dict with the NEW absolute values (counts, ids...)
    """
    payload = {
        "type": "social_action",  # -> SocialConsumer.social_action
        "action": action,
        "target_id": target_id,
        "data": data or {},
    }
    # Send only after the DB transaction is committed, so clients that
    # re-fetch immediately always see the fresh data.
    transaction.on_commit(lambda: _group_send(GLOBAL_GROUP, payload))


def push_notification_signal(recipient_id):
    """Tell one user that their notifications changed (new or removed)."""
    payload = {
        "type": "notification_push",  # -> SocialConsumer.notification_push
        "target_id": recipient_id,
    }
    transaction.on_commit(lambda: _group_send(user_group(recipient_id), payload))


def push_message_signal(recipient_id):
    """Tell one user that their unread-messages count changed (new message
    received, or messages read from another tab)."""
    payload = {
        "type": "message_push",  # -> SocialConsumer.message_push
        "target_id": recipient_id,
    }
    transaction.on_commit(lambda: _group_send(user_group(recipient_id), payload))
