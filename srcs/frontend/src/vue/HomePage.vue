<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
import RChat from './RChat.vue';
import SearchBar from './SearchBar.vue';
import NotificationBell from './NotificationBell.vue';
import LanguageSwitcher from './LanguageSwitcher.vue';
import { t as $t } from '../i18n';
import { currentLang } from '../i18n';
import ChatNavLink from './ChatNavLink.vue';
import { useSocialSocket } from '../composables/useSocialSocket';

//--------------------xh start----------------
const props = defineProps({ mode: { type: String, default: 'for_you' } });
//-------------xh end----------------------------
// --- Video feed: real events published by the owners (GET /api/feed/) ---
const videos = ref([]);
const feedLoading = ref(true);
const activeIndex = ref(0);                        // which video is on screen
const activeEvent = computed(() => videos.value[activeIndex.value] || null);
const activeEventId = computed(() => (activeEvent.value ? activeEvent.value.id : null));
const wrapperRefs = [];                            // one DOM element per video


// Variable bach t7ell/t-sdd l-pop-up dyal l-informations
const showInfoModal = ref(false);
const openInfoModal = () => { showInfoModal.value = true; };
const closeInfoModal = () => { showInfoModal.value = false; };

const comments = ref([]);
const newCommentText = ref('');

// Controls global mute state
const isMuted = ref(true);

// Function to toggle audio for all videos
const toggleMute = () => {
  isMuted.value = !isMuted.value;
};

// Function to play or pause the video when clicked
const togglePlay = (event) => {
  const videoElement = event.target;
  if (videoElement.paused) {
    videoElement.play();
  } else {
    videoElement.pause();
  }
};

const getToken = () => sessionStorage.getItem('token') || sessionStorage.getItem('access') || sessionStorage.getItem('access_token');
const API = '/api';

// --- Comments state ---
const commentsListRef = ref(null);      // scrollable list element
const commentInputRef = ref(null);      // input element (to focus on reply)
const replyingTo = ref(null);           // { parentId, username } or null
const expandedReplies = reactive({});   // { [commentId]: true } when replies are open
const isSending = ref(false);

const scrollCommentsToBottom = async () => {
  await nextTick();
  const el = commentsListRef.value;
  if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
};

// Newest comments are at the TOP of the list
const scrollCommentsToTop = async () => {
  await nextTick();
  const el = commentsListRef.value;
  if (el) el.scrollTo({ top: 0, behavior: 'smooth' });
};

const timeAgo = (iso) => {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return 'now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d`;
  return `${Math.floor(diff / 604800)}w`;
};

// GET: Recupera i commenti (each top-level comment has its replies nested)
const fetchComments = async (eventId) => {
  const token = getToken();
  try {
    const response = await fetch(`${API}/social/events/${eventId}/comments/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      if (eventId !== activeEventId.value) return;
      comments.value = data
        .filter(c => !c.parent_comment)
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      scrollCommentsToTop();
    }
  } catch (error) {
    console.error('Errore durante il recupero dei commenti:', error);
  }
};

// Click on "Reply": show the "Replying to" bar and prefill @username
const startReply = (comment, rootComment) => {
  replyingTo.value = { parentId: rootComment.id, username: comment.user_username };
  newCommentText.value = `@${comment.user_username} `;
  nextTick(() => commentInputRef.value && commentInputRef.value.focus());
};

const cancelReply = () => {
  replyingTo.value = null;
  newCommentText.value = '';
};

const toggleReplies = (commentId) => {
  expandedReplies[commentId] = !expandedReplies[commentId];
};

const postComment = async () => {
  const text = newCommentText.value.trim();
  if (!text || isSending.value || !activeEventId.value) return;
  const token = getToken();
  const parentId = replyingTo.value ? replyingTo.value.parentId : null;
  isSending.value = true;

  try {
    const response = await fetch(`${API}/social/events/${activeEventId.value}/comments/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ content: text, parent_comment: parentId })
    });

    if (response.ok) {
      const added = await response.json();
      if (activeEvent.value) activeEvent.value.comments_count = (activeEvent.value.comments_count || 0) + 1;
      if (parentId) {
        const parent = comments.value.find(c => c.id === parentId);
        if (parent) {
          parent.replies = parent.replies || [];
          parent.replies.push(added);
          parent.reply_count = parent.replies.length;
          expandedReplies[parentId] = true;
        }
      } else {
        comments.value.unshift(added);
        scrollCommentsToTop();
      }
      newCommentText.value = '';
      replyingTo.value = null;
    } else {
      alert($t('commentSaveError'));
    }
  } catch (error) {
    console.error('Errore di rete durante l\'invio del commento:', error);
  } finally {
    isSending.value = false;
  }
};

// --- Reactions on comments ---
// Same list as Reaction.REACTION_CHOICES in the backend (type -> emoji)
const REACTIONS = [
  { type: 'like', emoji: '❤️' },
  { type: 'laugh', emoji: '😂' },
  { type: 'wow', emoji: '😮' },
  { type: 'sad', emoji: '😢' },
  { type: 'angry', emoji: '😡' },
  { type: 'thumbs_up', emoji: '👍' },
  { type: 'thumbs_down', emoji: '👎' },
];

// id of the comment whose emoji bar is open (null = none)
const openPicker = ref(null);
let pickerTimeout = null;

const showPicker = (id) => {
  if (pickerTimeout) {
    clearTimeout(pickerTimeout);
    pickerTimeout = null;
  }
  openPicker.value = id;
};

const hidePicker = () => {
  pickerTimeout = setTimeout(() => {
    openPicker.value = null;
  }, 200);
};

// Emoji for a type; no reaction (null) -> empty heart
const emojiOf = (type) => (REACTIONS.find(r => r.type === type) || {}).emoji || '🤍';

// Reactions that really exist on a comment, most used first: [{ type, emoji, n }]
const reactionList = (counts) =>
  Object.entries(counts || {})
    .filter(([, n]) => n > 0)
    .map(([type, n]) => ({ type, emoji: emojiOf(type), n }))
    .sort((a, b) => b.n - a.n);

const reactionTotal = (counts) =>
  Object.values(counts || {}).reduce((sum, n) => sum + (n || 0), 0);

const reactToComment = async (comment, type) => {
  if (pickerTimeout) {
    clearTimeout(pickerTimeout);
    pickerTimeout = null;
  }
  openPicker.value = null;
  try {
    const res = await fetch(`${API}/social/comments/${comment.id}/react/`, {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ reaction_type: type })
    });
    if (res.ok) {
      const data = await res.json();
      comment.user_reaction = data.user_reaction;
      comment.reactions_count = data.reactions_count;
    }
  } catch (error) {
    console.error('Errore durante la reaction:', error);
  }
};
// reaction
const formatCount = (n) => (n >= 1000 ? `${(n / 1000).toFixed(1).replace(/\.0$/, '')}k` : `${n || 0}`);

const authHeaders = () => ({ 'Authorization': `Bearer ${getToken()}` });

// Where the owner's name/avatar leads: own profile or the public profile page
const ownerLink = computed(() => {
  const owner = activeEvent.value && activeEvent.value.owner;
  if (!owner) return '/home';
  return owner.is_self ? '/profile' : { name: 'UserProfile', params: { id: owner.id } };
});

// POST like toggle for the video on screen
const toggleLike = async () => {
  const ev = activeEvent.value;
  if (!ev) return;
  try {
    const res = await fetch(`${API}/social/events/${ev.id}/like/`, { method: 'POST', headers: authHeaders() });
    if (res.ok) {
      const data = await res.json();
      ev.is_liked = data.is_liked;
      ev.likes_count = data.likes_count;
    }
  } catch (error) {
    console.error('Like failed:', error);
  }
};

// POST subscribe/unsubscribe to the owner of the video on screen
const toggleSubscribe = async () => {
  const ev = activeEvent.value;
  if (!ev || ev.owner.is_self) return;
  try {
    const res = await fetch(`${API}/social/follow/${ev.owner.id}/`, { method: 'POST', headers: authHeaders() });
    if (res.ok) {
      const data = await res.json();
      videos.value.forEach((v) => { if (v.owner.id === ev.owner.id) v.owner.is_following = data.is_following; });
    }
  } catch (error) {
    console.error('Subscribe failed:', error);
  }
};

let observer = null;
const setupObserver = async () => {
  await nextTick();
  if (observer) observer.disconnect();
  observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const video = entry.target.querySelector('video');
      if (entry.isIntersecting) {
        activeIndex.value = Number(entry.target.dataset.index);
        if (video) video.play().catch(() => {});
      } else if (video) {
        video.pause();
      }
    });
  }, { threshold: 0.6 });
  wrapperRefs.forEach((el) => el && observer.observe(el));
};

//-----------------xh add part start-----------------------------
const fetchFeed = async () => {
  feedLoading.value = true;
  videos.value = [];
  activeIndex.value = 0;
  try {
    const res = await fetch(`${API}/feed/?mode=${props.mode}`, { headers: authHeaders() });
    if (res.ok) {
      videos.value = await res.json();
      wrapperRefs.length = 0;
    }
  } catch (error) {
    console.error('Could not load the feed:', error);
  } finally {
    feedLoading.value = false;
  }
  await nextTick();
  setupObserver();
};

watch(() => props.mode, fetchFeed);
onMounted(fetchFeed);
//-----------------------xh add part end----------------------------
const findCommentById = (commentId) => {
  for (const comment of comments.value) {
    if (comment.id === commentId) return comment;
    const reply = (comment.replies || []).find((r) => r.id === commentId);
    if (reply) return reply;
  }
  return null;
};

const handleSocialMessage = (message) => {
  const { action, target_id: targetId, data } = message;

  if (action === 'like') {
    const ev = videos.value.find((v) => v.id === targetId);
    if (ev) ev.likes_count = data.likes_count;
  } else if (action === 'comment') {
    const ev = videos.value.find((v) => v.id === targetId);
    if (ev) ev.comments_count = data.comments_count;
    // Reload the open comment list, unless the comment is already on screen
    // (it is the one I just posted myself).
    if (targetId === activeEventId.value && !findCommentById(data.comment_id)) {
      fetchComments(targetId);
    }
  } else if (action === 'comment_reaction') {
    if (data.event_id !== activeEventId.value) return;
    const comment = findCommentById(targetId);
    if (comment) comment.reactions_count = data.reactions_count;

  } else if (action === 'update_profile') {
    videos.value.forEach((v) => {
      if (v.owner && v.owner.id === targetId) {
        v.owner.display_name = data.username || data['user.name'] || data.name || v.owner.display_name;
        v.owner.username = data.username || data['user.name'] || data.name || v.owner.username;
        const newAvatar = data.user_avatar || data.avatar_url || data.avatar;
        if (newAvatar) v.owner.avatar = newAvatar;
      }
    });
    comments.value.forEach((c) => {
      // Top-level comments
      if (c.user_id === targetId || (c.user && c.user.id === targetId)) {
        c.user_username = data.username || data['user.name'] || data.name || c.user_username;
        const newAvatar = data.user_avatar || data.avatar_url || data.avatar;
        if (newAvatar) c.user_avatar = newAvatar;
      }
      // Replies
      if (c.replies) {
        c.replies.forEach((r) => {
          if (r.user_id === targetId || (r.user && r.user.id === targetId)) {
            r.user_username = data.username || data['user.name'] || data.name || r.user_username;
            const newAvatar = data.user_avatar || data.avatar_url || data.avatar;
            if (newAvatar) r.user_avatar = newAvatar;
          }
        });
      }
    });

  } else if (action === 'resync') {
    if (activeEventId.value) fetchComments(activeEventId.value);
  }
};

useSocialSocket(handleSocialMessage);


watch(activeEventId, (id) => {
  comments.value = [];
  cancelReply();
  openPicker.value = null;
  Object.keys(expandedReplies).forEach((k) => delete expandedReplies[k]);
  if (id) fetchComments(id);
});

onMounted(fetchFeed);
onBeforeUnmount(() => {
  if (observer) observer.disconnect();
  if (pickerTimeout) clearTimeout(pickerTimeout);
});
</script>

<template>
  <video autoplay muted loop playsinline id="bgVideo">
    <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
  </video>

  <div class="app-container">
    <header class="navbar glass-panel">
      <div class="logo">
        <img src="../assets/logo_temp.png" alt="Ready2Roll Logo" class="nav-logo-img">
        <span class="logo-text">Ready2Roll</span>
      </div>
      <SearchBar />
      <div class="nav-icons">
        <LanguageSwitcher />
        <NotificationBell />
        <ChatNavLink>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
          </svg>
        </ChatNavLink>
        <router-link to="/profile" class="nav-icon-link">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
        </router-link>
      </div>
    </header>

    <div class="main-content">
      <aside class="left-sidebar glass-panel">
        <nav class="main-menu">
          <h3>{{ $t('menu') }}</h3>
          <ul>
            <li @click="$router.push('/home')" class="menu-item">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="menu-svg-icon"
              >
                <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/>
                <path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              </svg>
              <span>{{ $t('forYou') }}</span>
            </li>
            <li @click="$router.push('/subscriptions')" class="menu-item">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="menu-svg-icon"
              >
                <path d="M16.051 12.616a1 1 0 0 1 1.909.024l.737 1.452a1 1 0 0 0 .737.535l1.634.256a1 1 0 0 1 .588 1.806l-1.172 1.168a1 1 0 0 0-.282.866l.259 1.613a1 1 0 0 1-1.541 1.134l-1.465-.75a1 1 0 0 0-.912 0l-1.465.75a1 1 0 0 1-1.539-1.133l.258-1.613a1 1 0 0 0-.282-.866l-1.156-1.153a1 1 0 0 1 .572-1.822l1.633-.256a1 1 0 0 0 .737-.535z"/>
                <path d="M8 15H7a4 4 0 0 0-4 4v2"/><circle cx="10" cy="7" r="4"/>
              </svg>
              <span>{{ $t('subscriptions') }}</span>
            </li>
            <li @click="$router.push('/discover')" class="menu-item">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="menu-svg-icon">
                  <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                  <path d="M8 16l2 -6l6 -2l-2 6l-6 2" />
                  <path d="M3 12a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
                  <path d="M12 3l0 2" />
                  <path d="M12 19l0 2" />
                  <path d="M3 12l2 0" />
                  <path d="M19 12l2 0" />
                </svg>
              <span>{{ $t('discover') }}</span>
            </li>
          </ul>
        </nav>
        <div class="sidebar-legal-footer" style="margin-top: auto; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.12); display: flex; gap: 10px; justify-content: center; font-size: 0.78rem;">
        <router-link to="/privacy" style="color: rgba(255,255,255,0.65); text-decoration: none;">{{ $t('privacy') }}</router-link>
        <span style="color: rgba(255,255,255,0.35);">·</span>
        <router-link to="/terms" style="color: rgba(255,255,255,0.65); text-decoration: none;">{{ $t ('term')}}</router-link>
      </div>
      </aside>

      <main class="feed-container">
        <div v-if="!feedLoading && videos.length === 0" class="empty-state">
          <div class="r-stage">
            <span class="r-glow"></span>
            <span class="r-ring r-ring-1"></span>
            <span class="r-ring r-ring-2"></span>
            <span class="r-orbit" style="--d: 7s; --s: 1;"><i></i></span>
            <span class="r-orbit" style="--d: 11s; --s: -1; inset: 18px;"><i></i></span>
            <span class="r-orbit" style="--d: 9s; --s: 1; inset: 36px; animation-delay: -3s;"><i></i></span>
            <div class="r-pop">
              <div class="r-float">
                <img src="../assets/logo_temp.png" alt="Ready2Roll" class="r-img">
                <span class="r-shine"></span>
              </div>
            </div>
          </div>
          <h2 class="empty-title">Ready2Roll</h2>
          <p class="empty-sub">No events yet. Owners will publish their events here.</p>
        </div>

        <div
          class="video-wrapper glass-panel"
          v-for="(video, index) in videos"
          :key="video.id"
          :data-index="index"
          :ref="el => { if (el) wrapperRefs[index] = el }"
        >
          <img v-if="video.media_type === 'image'" :src="video.media_src" :alt="video.title" class="feed-video">
          <video
            v-else
            class="feed-video"
            :src="video.media_src"
            loop
            :muted="isMuted"
            playsinline
            @click="togglePlay">
          </video>
          <div class="video-overlay">
            <h2>{{ video.title }}</h2>
          </div>
          <div class="video-controls" v-if="video.media_type !== 'image'">
            <button class="volume-btn" @click="toggleMute">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="video-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z" />
              </svg>
            </button>
          </div>
        </div>
      </main>

      <aside class="right-sidebar">
        <template v-if="activeEvent">
          <div class="owner-info glass-panel">
            <div class="owner-header">
              <router-link :to="ownerLink" class="owner-link">
                <img :src="activeEvent.owner.avatar" alt="owner" class="avatar">
                <div class="owner-text">
                  <p class="owner-name">{{ activeEvent.owner.display_name }}</p>
                  <p class="owner-handle">@{{ activeEvent.owner.username }} · {{ timeAgo(activeEvent.created_at) }}</p>
                </div>
              </router-link>
              <button
                v-if="!activeEvent.owner.is_self"
                class="subscribe-btn"
                :class="{ subscribed: activeEvent.owner.is_following }"
                @click="toggleSubscribe">
                {{ activeEvent.owner.is_following ? $t('Followed') :  $t('Follow') }}
              </button>
            </div>
            <p class="description">{{ activeEvent.description }}</p>
          </div>

          <div class="action-buttons glass-panel" style="display: flex; justify-content: space-between; padding: 10px; gap: 8px;">
            <!-- LIKES BUTTON -->
              <button :class="{ liked: activeEvent.is_liked }" @click="toggleLike" style="display: flex; align-items: center; justify-content: center; gap: 6px; flex: 1; padding: 8px 0;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" :fill="activeEvent.is_liked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-heart">
                  <path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"/>
                </svg>
                {{ formatCount(activeEvent.likes_count) }}
              </button>
              <!-- SHOW INFORMATIONS BUTTON (B7alhom f size) -->
              <button class="show-info-btn" @click="openInfoModal" style="display: flex; align-items: center; justify-content: center; gap: 6px; flex: 1; padding: 8px 0; border: none; background: rgba(0, 242, 254, 0.15); color: #00f2fe; border-radius: 10px; cursor: pointer;">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-info"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
                <span style="font-size: 0.75rem; font-weight: bold;">Info</span>
              </button>
              <!-- COMMENTS BUTTON -->
              <button style="display: flex; align-items: center; justify-content: center; gap: 6px; flex: 1; padding: 8px 0;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-message-circle-more">
                  <path d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719"/>
                  <path d="M8 12h.01"/><path d="M12 12h.01"/><path d="M16 12h.01"/>
                </svg>
                {{ formatCount(activeEvent.comments_count) }}
              </button>
          </div>
          <div class="comments-section glass-panel">
            <h3>{{ $t('comments') }}</h3>
            <!-- Scrollable list: newest comment is at the bottom, right above the input -->
            <div class="comments-list" ref="commentsListRef">
              <p v-if="comments.length === 0" class="no-comments">{{ $t('noCommentsYet') }}</p>
              <div class="comment-thread" v-for="comment in comments" :key="comment.id">
                <div class="comment">
                  <img :src="comment.user_avatar" alt="avatar" class="avatar comment-avatar">
                  <div class="comment-body">
                    <p class="comment-line"><strong>{{ comment.user_username }}</strong> {{ comment.content }}</p>
                    <div class="comment-meta">
                      <span>{{ timeAgo(comment.created_at) }}</span>
                      <button class="reply-btn" @click="startReply(comment, comment)">{{ $t('reply') }}</button>
                      <!-- reaction -->
                      <div class="reaction-wrap" @mouseenter="showPicker(comment.id)" @mouseleave="hidePicker">
                        <button
                          type="button"
                          class="reaction-btn"
                          :class="{ active: comment.user_reaction }"
                          @click="reactToComment(comment, comment.user_reaction || 'like')"
                        >
                          {{ emojiOf(comment.user_reaction) }}
                        </button>
                        <div
                          class="reaction-picker"
                          v-if="openPicker === comment.id"
                          @mouseenter="showPicker(comment.id)"
                          @mouseleave="hidePicker"
                        >
                          <button
                            type="button"
                            v-for="r in REACTIONS"
                            :key="r.type"
                            @click.stop="reactToComment(comment, r.type)"
                          >
                            {{ r.emoji }}
                          </button>
                        </div>
                      </div>
                      <!-- all reactions in one chip; hover = every emoji with its count -->
                      <div class="reaction-stats" v-if="reactionTotal(comment.reactions_count) > 0" tabindex="0">
                        <span class="stats-emojis">
                          <span v-for="r in reactionList(comment.reactions_count).slice(0, 3)" :key="r.type">{{ r.emoji }}</span>
                        </span>
                        <span class="stats-total">{{ formatCount(reactionTotal(comment.reactions_count)) }}</span>
                        <div class="stats-pop">
                          <div v-for="r in reactionList(comment.reactions_count)" :key="r.type" class="stats-item" :class="{ mine: comment.user_reaction === r.type }">
                            <span class="stats-emoji">{{ r.emoji }}</span>
                            <span class="stats-n">{{ formatCount(r.n) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <!-- reaction -->
                    <button
                      v-if="comment.reply_count > 0"
                      class="view-replies-btn"
                      @click="toggleReplies(comment.id)">
                      <span class="replies-line"></span>
                      {{ expandedReplies[comment.id] ? $t('hideReplies') : `${$t('viewReplies')} ${comment.reply_count}` }}
                    </button>
                    <div v-if="expandedReplies[comment.id]" class="replies">
                      <div class="comment reply" v-for="reply in comment.replies" :key="reply.id">
                        <img :src="reply.user_avatar" alt="avatar" class="avatar reply-avatar">
                        <div class="comment-body">
                          <p class="comment-line"><strong>{{ reply.user_username }}</strong> {{ reply.content }}</p>
                          <div class="comment-meta">
                            <span>{{ timeAgo(reply.created_at) }}</span>
                            <button class="reply-btn" @click="startReply(reply, comment)">{{ $t('reply') }}</button>
                            <div class="reaction-wrap" @mouseenter="showPicker(reply.id)" @mouseleave="hidePicker">
                              <button
                                type="button"
                                class="reaction-btn"
                                :class="{ active: reply.user_reaction }"
                                @click="reactToComment(reply, reply.user_reaction || 'like')"
                              >
                                {{ emojiOf(reply.user_reaction) }}
                              </button>
                              <div
                                class="reaction-picker"
                                v-if="openPicker === reply.id"
                                @mouseenter="showPicker(reply.id)"
                                @mouseleave="hidePicker"
                              >
                                <button
                                  type="button"
                                  v-for="r in REACTIONS"
                                  :key="r.type"
                                  @click.stop="reactToComment(reply, r.type)"
                                >
                                  {{ r.emoji }}
                                </button>
                              </div>
                              </div>
                              <div class="reaction-stats" v-if="reactionTotal(reply.reactions_count) > 0" tabindex="0">
                                <span class="stats-emojis">
                                  <span v-for="r in reactionList(reply.reactions_count).slice(0, 3)" :key="r.type">{{ r.emoji }}</span>
                                </span>
                                <span class="stats-total">{{ formatCount(reactionTotal(reply.reactions_count)) }}</span>
                                <div class="stats-pop">
                                  <div v-for="r in reactionList(reply.reactions_count)" :key="r.type" class="stats-item" :class="{ mine: reply.user_reaction === r.type }">
                                    <span class="stats-emoji">{{ r.emoji }}</span>
                                    <span class="stats-n">{{ formatCount(r.n) }}</span>
                                  </div>
                                </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="comment-composer">
              <div v-if="replyingTo" class="replying-bar">
                <span>{{ $t('replyingTo') }} <strong>@{{ replyingTo.username }}</strong></span>
                <button class="cancel-reply" @click="cancelReply" aria-label="Cancel reply">✕</button>
              </div>
              <div class="add-comment-area">
                <input
                  ref="commentInputRef"
                  type="text"
                  v-model="newCommentText"
                  :placeholder="replyingTo ? $t('reply') + '...' : $t('addComment')"
                  @keyup.enter="postComment"
                  class="comment-input"
                  :dir="currentLang === 'ar' ? 'rtl' : 'ltr'"
                />
                <button @click="postComment" class="send-comment-btn" :disabled="isSending || !newCommentText.trim()">{{ $t('post') }}</button>
              </div>
            </div>
          </div>
        </template>
      </aside>
    </div>
  </div>

  <!-- MODAL DYAL SHOW INFORMATIONS -->
  <div v-if="showInfoModal && activeEvent" class="modal-overlay" @click.self="closeInfoModal">
    <div class="info-modal-card glass-panel">
      <div class="modal-header">
        <h3 style="margin: 0;">Event Informations</h3>
        <button class="close-modal-btn" @click="closeInfoModal">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>
      <div class="modal-body info-modal-body">

        <div class="info-row">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-map-pin ui-icon"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>
          <div class="info-text-block">
            <strong>{{ $t('location') }}</strong>
            <span>{{ activeEvent.location || $t('locationTBD') }}</span>
          </div>
        </div>

        <div class="info-row">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calendar-days ui-icon"><path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M8 13h.01"/><path d="M12 13h.01"/><path d="M16 13h.01"/><path d="M8 17h.01"/><path d="M12 17h.01"/><path d="M16 17h.01"/></svg>
          <div class="info-text-block">
            <strong>{{ $t('date') }}</strong>
            <span>{{ activeEvent.event_date ? activeEvent.event_date.slice(0, 16).replace('T', ' ') : 'TBD' }}</span>
          </div>
        </div>

        <div class="info-row">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-ticket ui-icon"><path d="M15 5v2"/><path d="M15 11v2"/><path d="M15 17v2"/><path d="M5 5h14a2 2 0 0 1 2 2v3a2 2 0 0 0 0 4v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3a2 2 0 0 0 0-4v-3a2 2 0 0 1 2-2z"/></svg>
          <div class="info-text-block">
            <strong>{{ $t('ticketPrice') }}</strong>
            <span>{{ activeEvent.ticket_price ? '€' + activeEvent.ticket_price : $t('free') }}</span>
          </div>
        </div>

        <div class="info-row">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-users ui-icon"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><path d="M16 3.128a4 4 0 0 1 0 7.744"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><circle cx="9" cy="7" r="4"/></svg>
          <div class="info-text-block">
            <strong>{{ $t('maxCapacity') }}</strong>
            <span>{{ activeEvent.max_capacity || '∞' }}</span>
          </div>
        </div>

        <div class="info-row tags-info-row">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ui-icon"><path d="M20.59 13.41 11 3.83V3H4v7h.83l9.58 9.59a2 2 0 0 0 2.83 0l3.35-3.35a2 2 0 0 0 0-2.83Z"/><circle cx="7.5" cy="7.5" r=".5"/></svg>
          <div class="info-text-block tags-info-block">
            <strong>Event Tags</strong>
            <div v-if="activeEvent.tags?.length" class="event-info-tags">
              <span v-for="tag in activeEvent.tags" :key="tag" class="event-info-tag"># {{ tag }}</span>
            </div>
            <span v-else class="no-event-tags">No tags added by the owner</span>
          </div>
        </div>

      </div>
    </div>
  </div>
<RChat :event-id="activeEvent ? activeEvent.id : null" />
</template>

<style scoped>
.feed-video { width: 100%; height: 100%; object-fit: cover; border-radius: 15px; position: absolute; top: 0; left: 0; z-index: 0; }
.video-overlay, .video-controls { position: relative; z-index: 1; }
.video-overlay { position: absolute; bottom: 30px; left: 20px; color: white; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); }
#bgVideo { position: fixed; top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; z-index: -1; object-fit: cover; }
.app-container { display: flex; flex-direction: column; height: 100vh; color: #FFFFFF; font-family: var(--font-main); padding: 10px 20px; box-sizing: border-box; }
.glass-panel { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; box-sizing: border-box; }
.navbar { display: flex; justify-content: space-between; align-items: center; height: 60px; margin-bottom: 15px; flex-shrink: 0; border: 1px solid rgba(255, 255, 255, 0.15); }
.search-bar input { background: rgba(255, 255, 255, 0.1); border: none; border-radius: 17px; padding: 10px 20px; color: white; width: 300px; }
.main-content { display: flex; flex-direction: row; justify-content: space-between; width: 100%; height: calc(100vh - 95px); overflow: hidden; }
.left-sidebar { width: 280px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
.right-sidebar { width: 320px; display: flex; flex-direction: column; gap: 15px; overflow: hidden; min-height: 0; }
.owner-info, .action-buttons { flex-shrink: 0; }
.feed-container { flex-grow: 1; max-width: 550px; height: 100%; overflow-y: scroll; scroll-snap-type: y mandatory; scroll-behavior: smooth; scrollbar-width: none; display: flex; flex-direction: column; }
.video-wrapper { min-height: 100%; width: 100%; scroll-snap-align: start; scroll-snap-stop: always; position: relative; display: flex; justify-content: center; align-items: center; border-radius: 15px; margin-bottom: 15px; }
.video-placeholder { text-align: center; color: rgba(255, 255, 255, 0.7); }
.video-controls { position: absolute; right: 15px; bottom: 20px; display: flex; flex-direction: column; gap: 10px; }
.video-controls button { background: rgba(0, 0, 0, 0.5); border: none; color: white; width: 35px; height: 35px; border-radius: 50%; cursor: pointer; }
ul { list-style: none; padding: 0; }
li { display: flex; align-items: center; gap: 10px; margin-bottom: 15px; cursor: pointer; }
.avatar { width: 40px; height: 40px; border-radius: 50%; }
.subscribe-btn { background: rgba(0, 242, 254, 0.7); color: white; border: none; border-radius: 10px; padding: 8px 15px; cursor: pointer; font-weight: bold; }
.owner-header { display: flex; align-items: center; gap: 10px; }
.action-buttons { display: flex; justify-content: space-around; }
.action-buttons button { background: rgba(255, 255, 255, 0.1); border: none; color: white; padding: 10px; border-radius: 10px; cursor: pointer; }
.logo { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.nav-logo-img { height: 35px; width: auto; object-fit: contain; }
.logo-text { font-family: "Bruno Ace", sans-serif; font-weight: bold; font-size: 1.2rem; color: #FFFFFF; }
.nav-icons { display: flex; gap: 20px; align-items: center; }
.nav-icon { width: 26px; height: 26px; color: #FFFFFF; cursor: pointer; transition: all 0.3s ease; }
.nav-icon:hover { color: #00f2fe; transform: scale(1.15); }
.main-menu ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 5px; }
.menu-item { display: flex; align-items: center; padding: 12px 15px; color: #FFFFFF; text-decoration: none; border-radius: 10px; transition: all 0.2s ease-in-out; cursor: pointer; }
.menu-item:hover { background: rgba(255, 255, 255, 0.1); }
.router-link-active { background: rgba(0, 242, 254, 0.15); color: #00f2fe; font-weight: bold; border-left: 4px solid #00f2fe; }
.volume-btn { background: rgba(0, 0, 0, 0.4); border: none; border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; cursor: pointer; transition: all 0.2s ease-in-out; position: absolute; bottom: 20px; right: 20px; }
.volume-btn:hover { background: rgba(0, 242, 254, 0.4); transform: scale(1.1); }
.video-icon { width: 22px; height: 22px; color: white; }
.user-link {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #FFFFFF;
  width: 100%;
}
.user-link:hover {
  color: #00f2fe;
}

.comments-section { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.comments-section h3 { margin: 0 0 10px; flex-shrink: 0; }
.comments-list { flex: 1; min-height: 0; overflow-y: auto; padding-right: 4px; scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.3) transparent; }
.no-comments { color: rgba(255,255,255,0.6); font-size: 13px; text-align: center; margin-top: 20px; }
.comment { display: flex; gap: 10px; margin-bottom: 14px; font-size: 14px; }
.comment-avatar { width: 32px; height: 32px; flex-shrink: 0; object-fit: cover; }
.reply-avatar { width: 24px; height: 24px; flex-shrink: 0; object-fit: cover; }
.comment-body { min-width: 0; flex: 1; }
.comment-line { margin: 0; line-height: 1.35; word-break: break-word; }
.comment-meta { position: relative; display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: center; margin-top: 3px; font-size: 12px; color: rgba(255,255,255,0.6); }
.reply-btn, .view-replies-btn, .cancel-reply { background: none; border: none; color: rgba(255,255,255,0.6); cursor: pointer; font-size: 12px; font-weight: bold; padding: 0; }
.reply-btn:hover, .view-replies-btn:hover { color: #00f2fe; }
.view-replies-btn { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
.replies-line { display: inline-block; width: 24px; height: 1px; background: rgba(255,255,255,0.4); }
.replies { margin-top: 10px; }
.replies .comment { margin-bottom: 10px; font-size: 13px; }
.reaction-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.reaction-btn { background: none; border: none; cursor: pointer; font-size: 14px; padding: 0; opacity: 0.7; }
.reaction-btn:hover, .reaction-btn.active { opacity: 1; }
/* One compact chip: top 3 emojis + total. Hover = popover with every emoji and its count */
.reaction-stats { position: relative; display: inline-flex; align-items: center; gap: 5px; padding: 1px 7px; border-radius: 10px; background: rgba(255,255,255,0.08); cursor: default; outline: none; transition: background 0.15s ease; }
.reaction-stats:hover, .reaction-stats:focus-visible { background: rgba(255,255,255,0.18); }
.stats-emojis { display: inline-flex; font-size: 12px; }
.stats-emojis span + span { margin-left: -4px; }
.stats-total { font-size: 12px; font-weight: bold; color: rgba(255,255,255,0.9); }
.stats-pop {
  position: absolute; left: 0; top: calc(100% + 6px); z-index: 20;
  display: flex; flex-wrap: wrap; gap: 4px; width: max-content; max-width: 200px; padding: 6px 8px;
  background: rgba(25, 25, 25, 0.97); border: 1px solid rgba(255,255,255,0.15); border-radius: 14px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.45);
  opacity: 0; visibility: hidden; pointer-events: none;
  transform: translateY(-4px) scale(0.96); transform-origin: top left;
  transition: opacity 0.15s ease, transform 0.18s ease, visibility 0.15s;
}
.reaction-stats:hover .stats-pop, .reaction-stats:focus-visible .stats-pop { opacity: 1; visibility: visible; transform: none; }
.stats-item { display: flex; flex-direction: column; align-items: center; min-width: 32px; padding: 3px 4px; border-radius: 10px; }
.stats-emoji { font-size: 18px; line-height: 1.15; }
.stats-n { font-size: 11px; font-weight: bold; color: rgba(255,255,255,0.85); }
.stats-item.mine { background: rgba(0,242,254,0.18); box-shadow: inset 0 0 0 1px rgba(0,242,254,0.6); }

.comments-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 4px;
  padding-bottom: 80px;
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.3) transparent;
}

.reaction-picker {
  position: absolute;
  left: -40px;
  top: calc(100% + 4px);
  z-index: 20;
  display: flex;
  gap: 4px;
  min-width: max-content;
  background: rgba(25, 25, 25, 0.97);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 14px;
  padding: 4px 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}
.reaction-picker button { background: none; border: none; cursor: pointer; font-size: 16px; padding: 0 2px; transition: transform 0.1s; }
.reaction-picker button:hover { transform: scale(1.3); }
.comment-composer { flex-shrink: 0; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.15); }
.replying-bar { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: rgba(255,255,255,0.75); background: rgba(255,255,255,0.08); border-radius: 8px; padding: 6px 10px; margin-bottom: 8px; }
.cancel-reply { font-size: 14px; }
.add-comment-area { display: flex; gap: 10px; }
.comment-input { flex-grow: 1; min-width: 0; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 17px; padding: 8px 15px; color: white; outline: none; }
.comment-input:focus { border-color: #00f2fe; }
.send-comment-btn { background: #00f2fe; color: #000; border: none; border-radius: 10px; padding: 8px 15px; font-weight: bold; cursor: pointer; }
.send-comment-btn:disabled { opacity: 0.4; cursor: default; }
.owner-link { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; color: #FFFFFF; text-decoration: none; }
.owner-link:hover .owner-name { color: #00f2fe; }
.owner-text { min-width: 0; }
.owner-name { margin: 0; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.owner-handle { margin: 2px 0 0; font-size: 12px; color: rgba(255,255,255,0.65); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.owner-info .avatar { width: 40px; height: 40px; object-fit: cover; flex-shrink: 0; }
.owner-info .description { margin: 10px 0 0; font-size: 14px; word-break: break-word; max-height: 90px; overflow-y: auto; }
.subscribe-btn.subscribed { background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.5); }
.action-buttons button.liked { background: rgba(255, 71, 87, 0.35); }
.empty-feed { text-align: center; color: rgba(255,255,255,0.75); margin: auto; }

/* ---------- Empty state: animated R ---------- */
.empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; text-align: center; }
.r-stage { position: relative; width: 280px; height: 280px; display: flex; align-items: center; justify-content: center; }
.r-pop, .r-float { position: relative; width: 170px; height: 170px; }
.r-pop { animation: r-intro 1.6s cubic-bezier(.2, 1.3, .35, 1) both; }
.r-float { animation: r-float 5s ease-in-out 1.6s infinite; transform-style: preserve-3d; }
.r-img { width: 100%; height: 100%; object-fit: contain; display: block; filter: drop-shadow(0 12px 28px rgba(255, 51, 187, 0.55)); }
.r-shine {
  position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(115deg, transparent 38%, rgba(255, 255, 255, 0.9) 50%, transparent 62%);
  background-size: 300% 100%;
  background-repeat: no-repeat;
  -webkit-mask: url('../assets/logo_temp.png') center / contain no-repeat;
  mask: url('../assets/logo_temp.png') center / contain no-repeat;
  mix-blend-mode: soft-light;
  animation: r-shine 3.6s ease-in-out 2s infinite;
}
.r-glow {
  position: absolute; width: 230px; height: 230px; border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 51, 187, 0.55) 0%, rgba(147, 51, 255, 0.35) 45%, transparent 70%);
  filter: blur(18px);
  animation: r-glow 3.2s ease-in-out infinite;
}
.r-ring { position: absolute; border-radius: 50%; border: 2px solid transparent; }
.r-ring-1 { inset: 20px; border-top-color: rgba(0, 242, 254, 0.9); border-right-color: rgba(0, 242, 254, 0.25); animation: r-spin 4s linear infinite, r-fade-in 1s ease 0.8s both; }
.r-ring-2 { inset: 0; border-bottom-color: rgba(255, 51, 187, 0.9); border-left-color: rgba(255, 51, 187, 0.2); animation: r-spin 6.5s linear infinite reverse, r-fade-in 1s ease 1s both; }
.r-orbit { position: absolute; inset: 0; animation: r-spin var(--d, 8s) linear infinite; animation-direction: normal; }
.r-orbit i { position: absolute; top: 0; left: 50%; width: 8px; height: 8px; margin-left: -4px; border-radius: 50%; background: #fff; box-shadow: 0 0 10px 3px rgba(0, 242, 254, 0.9), 0 0 22px 6px rgba(255, 51, 187, 0.6); animation: r-twinkle 1.8s ease-in-out infinite; }
.empty-title {
  margin: 0; font-family: "Bruno Ace", sans-serif; font-size: 1.6rem; letter-spacing: 2px;
  background: linear-gradient(90deg, #ff33bb, #9333ff, #00f2fe, #ff33bb); background-size: 300% 100%;
  -webkit-background-clip: text; background-clip: text; color: transparent;
  animation: r-text-slide 5s linear infinite, r-rise 0.9s ease 1.2s both;
}
.empty-sub { margin: 0; color: rgba(255, 255, 255, 0.75); font-size: 14px; animation: r-rise 0.9s ease 1.5s both; }

@keyframes r-intro {
  0%   { transform: scale(0) rotate(-540deg); opacity: 0; filter: blur(10px); }
  60%  { opacity: 1; filter: blur(0); }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}
@keyframes r-float {
  0%, 100% { transform: translateY(0) rotateY(0deg) rotateZ(-2deg); }
  25%      { transform: translateY(-14px) rotateY(18deg) rotateZ(0deg); }
  50%      { transform: translateY(0) rotateY(0deg) rotateZ(2deg); }
  75%      { transform: translateY(-10px) rotateY(-18deg) rotateZ(0deg); }
}
@keyframes r-shine { 0% { background-position: 130% 0; } 55%, 100% { background-position: -30% 0; } }
@keyframes r-glow { 0%, 100% { transform: scale(0.9); opacity: 0.7; } 50% { transform: scale(1.15); opacity: 1; } }
@keyframes r-spin { to { transform: rotate(360deg); } }
@keyframes r-fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes r-twinkle { 0%, 100% { opacity: 0.35; transform: scale(0.7); } 50% { opacity: 1; transform: scale(1.2); } }
@keyframes r-text-slide { to { background-position: 300% 0; } }
@keyframes r-rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

@media (prefers-reduced-motion: reduce) {
  .r-pop, .r-float, .r-shine, .r-glow, .r-ring, .r-orbit, .r-orbit i, .empty-title, .empty-sub { animation: none !important; }
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.menu-svg-icon {
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.7);
  transition: color 0.2s ease, transform 0.2s ease;
}

.menu-item:hover .menu-svg-icon {
  color: #00f2fe;
  transform: scale(1.1);
}

.event-quick-stats {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 10px;
  flex-shrink: 0;
}

.quick-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
  text-align: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px 4px;
  transition: all 0.2s ease;
  cursor: default;
}

.quick-stat:hover {
  background: rgba(0, 242, 254, 0.12);
  border-color: rgba(0, 242, 254, 0.4);
  transform: translateY(-2px);
}

.stat-text {
  font-size: 0.68rem;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
  font-weight: bold;
}

.quick-stat .ui-icon {
  color: #00f2fe;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(2px);
  z-index: 9999;
}

.info-modal-card {
  position: fixed;
  top: 50%;
  right: 350px;
  transform: translateY(-50%);
  width: 320px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  box-sizing: border-box;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  padding: 0;
  display: flex;
  flex-direction: column;
  color: #fff;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.info-modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.05);
  padding: 12px 18px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.info-row:hover {
  background: rgba(255, 255, 255, 0.15);
}

.info-text-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}


.tags-info-row { align-items: flex-start; }
.tags-info-block { min-width: 0; width: 100%; }
.event-info-tags { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 7px; }
.event-info-tag {
  display: inline-flex; align-items: center;
  padding: 5px 10px; border-radius: 999px;
  color: #00f2fe; font-size: 12px; font-weight: 700;
  background: rgba(0, 242, 254, 0.12);
  border: 1px solid rgba(0, 242, 254, 0.35);
  box-shadow: 0 0 10px rgba(0, 242, 254, 0.08);
}
.no-event-tags { opacity: .65; font-size: 13px; }

[dir="rtl"] .info-modal-card {
  right: auto;
  left: 350px;
}

@media (max-width: 1200px) {
  .info-modal-card {
    right: 50%;
    transform: translate(50%, -50%);
  }
  [dir="rtl"] .info-modal-card {
    left: 50%;
    transform: translate(-50%, -50%);
  }
}
@media (max-width: 1024px) {
  .feed-container {
    width: 100%;
    max-width: 100%;
    height: 70vh;
    flex-shrink: 0;
    overflow-y: scroll;
    scroll-snap-type: y mandatory;
  }

  .video-wrapper {
    height: 100%;
    min-height: 100%;
    flex-shrink: 0;
  }
}

</style>
