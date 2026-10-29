import random
from itertools import islice
from django.db.models import Count
from .models import Event

FEED_SIZE = 30
TAG_SHARE = 0.8
TREND_SHARE = 0.7


def _valid_events():
    return (Event.objects
            .filter(status__iexact='active', media__media_url__isnull=False)
            .exclude(media__media_url='')
            .distinct())


def _shuffle(items):
    items = list(items)
    random.shuffle(items)
    return items


def _trending(qs, exclude_ids=()):
    return list(qs.exclude(id__in=exclude_ids)
                  .annotate(n=Count('likes', distinct=True))
                  .order_by('-n', '-created_at')
                  .values_list('id', flat=True))


def _interleave(main, extra, every):
    """Dopo ogni (every-1) elementi di main inserisce uno di extra."""
    main_it, extra_it, out = iter(main), iter(extra), []
    while True:
        chunk = list(islice(main_it, every - 1))
        e = next(extra_it, None)
        out += chunk
        if e is not None:
            out.append(e)
        if not chunk and e is None:
            return out


class _Picker:
    """Prende id senza duplicati."""
    def __init__(self):
        self.seen = set()

    def take(self, source, n):
        out = []
        for i in source:
            if len(out) >= n:
                break
            if i not in self.seen:
                self.seen.add(i)
                out.append(i)
        return out


def for_you_ids(user, size=FEED_SIZE):
    base = _valid_events().exclude(organizer=user)
    my_tags = set(user.tags.values_list('id', flat=True))
    liked = Event.objects.filter(likes__user=user)
    liked_ids = set(liked.values_list('id', flat=True))
    liked_tags = set(liked.values_list('tags', flat=True)) - {None}
    liked_orgs = set(liked.values_list('organizer_id', flat=True))

    tag_ids = []
    if my_tags:
        rows = (base.filter(tags__in=my_tags)
                    .annotate(match=Count('tags', distinct=True))
                    .values_list('id', 'match'))
        tag_ids = [r[0] for r in sorted(rows, key=lambda r: (-r[1], random.random()))]

    like_ids = []
    if liked_tags or liked_orgs:
        from django.db.models import Q
        q = Q(tags__in=liked_tags) | Q(organizer_id__in=liked_orgs)
        like_ids = _shuffle(base.filter(q).exclude(id__in=liked_ids)
                                .values_list('id', flat=True))

    n_tags = round(size * TAG_SHARE)
    pick = _Picker()
    a = pick.take(tag_ids, n_tags)
    b = pick.take(like_ids, size - n_tags)
    a += pick.take(tag_ids, size - len(a) - len(b))
    b += pick.take(like_ids, size - len(a) - len(b))
    fill = pick.take(_trending(base, liked_ids), size - len(a) - len(b))
    return _interleave(a, b, every=5) + fill


def discover_ids(user, size=FEED_SIZE):
    base = _valid_events().exclude(organizer=user)
    my_tags = set(user.tags.values_list('id', flat=True))
    liked_ids = set(user.event_likes.values_list('event_id', flat=True))

    n_trend = round(size * TREND_SHARE)
    trending = _trending(base, liked_ids)
    trend_pool = _shuffle(trending[:n_trend * 3])

    explore = _shuffle(base.exclude(tags__in=my_tags).exclude(id__in=liked_ids)
                           .values_list('id', flat=True))

    pick = _Picker()
    a = pick.take(trend_pool, n_trend)
    b = pick.take(explore, size - n_trend)
    a += pick.take(trending, size - len(a) - len(b))
    return _interleave(a, b, every=3)

def following_ids(user, size=FEED_SIZE * 3):
    """Solo eventi di chi segui, dal più recente."""
    followed = user.following.values_list('followed_id', flat=True)
    return list(_valid_events()
                .filter(organizer_id__in=followed)
                .order_by('-created_at')
                .values_list('id', flat=True))[:size]

def build_feed(user, mode):
	if mode == 'following':
		return following_ids(user)
	ids = discover_ids(user) if mode == 'discover' else for_you_ids(user)
	if not ids:
		ids = _trending(_valid_events())[:FEED_SIZE]
	return ids
