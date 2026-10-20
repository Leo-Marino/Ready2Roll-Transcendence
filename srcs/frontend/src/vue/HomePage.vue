<script setup>
// 1. ADDED: onMounted import
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';

// (Mock Data for Left Sidebar)
const subscribedAccounts = ref([
  { id: 1, name: 'Xhul', img: 'https://i.pravatar.cc/150?u=1' },
  { id: 2, name: 'Anna', img: 'https://i.pravatar.cc/150?u=2' },
  { id: 3, name: 'thilina', img: 'https://i.pravatar.cc/150?u=3' }
]);

// (Mock Data for Right Sidebar Comments)
// const comments = ref([
//   { id: 1, user: 'Xhul', text: 'The drop on that first track was insanity!' },
//   { id: 2, user: 'Anna', text: 'Best set of the year so far!' }
// ]);

// --- Video feed: real events published by the owners (GET /api/feed/) ---
const videos = ref([]);
const feedLoading = ref(true);
const activeIndex = ref(0);                       // which video is on screen
const activeEvent = computed(() => videos.value[activeIndex.value] || null);
const activeEventId = computed(() => (activeEvent.value ? activeEvent.value.id : null));
const wrapperRefs = [];                           // one DOM element per video

const comments = ref([]);
const newCommentText = ref('');

// Controls global mute state
const isMuted = ref(true);

// NEW: Function to toggle audio for all videos
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

const getToken = () => localStorage.getItem('token') || localStorage.getItem('access') || localStorage.getItem('access_token');
const API = '/api';
// --- Comments state ---
const commentsListRef = ref(null);     // scrollable list element
const commentInputRef = ref(null);     // input element (to focus on reply)
const replyingTo = ref(null);          // { parentId, username } or null
const expandedReplies = reactive({});  // { [commentId]: true } when replies are open
const isSending = ref(false);

const scrollCommentsToBottom = async () => {
  await nextTick();
  const el = commentsListRef.value;
  if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
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
      if (eventId !== activeEventId.value) return; // user already scrolled to another video
      comments.value = data;
      scrollCommentsToBottom();
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

// POST: Salva il nuovo commento (or reply)
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
        // New comment goes at the END: right above the input box
        comments.value.push(added);
        scrollCommentsToBottom();
      }
      newCommentText.value = '';
      replyingTo.value = null;
    } else {
      alert("Errore nel salvataggio del commento.");
    }
  } catch (error) {
    console.error('Errore di rete durante l\'invio del commento:', error);
  } finally {
    isSending.value = false;
  }
};
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
      // same owner can have several videos: keep them all in sync
      videos.value.forEach((v) => { if (v.owner.id === ev.owner.id) v.owner.is_following = data.is_following; });
    }
  } catch (error) {
    console.error('Subscribe failed:', error);
  }
};

// The "radar": the video that is >60% visible becomes the active one.
// It plays, the others pause, and the right panel (owner, stats, comments) follows it.
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

const fetchFeed = async () => {
  try {
    const res = await fetch(`${API}/feed/`, { headers: authHeaders() });
    if (res.ok) {
      videos.value = await res.json();
      wrapperRefs.length = 0;
    }
  } catch (error) {
    console.error('Could not load the feed:', error);
  } finally {
    feedLoading.value = false;
  }
  setupObserver();
};

// Scrolled to another video -> load ITS comments
watch(activeEventId, (id) => {
  comments.value = [];
  cancelReply();
  Object.keys(expandedReplies).forEach((k) => delete expandedReplies[k]);
  if (id) fetchComments(id);
});

onMounted(fetchFeed);
onBeforeUnmount(() => observer && observer.disconnect());
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
      <div class="search-bar">
        <input type="text" placeholder="Search...">
      </div>
      <div class="nav-icons">
        <router-link to="/chat" class="nav-icon-link">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
          </svg>
        </router-link>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 011.037-.443 48.282 48.282 0 005.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
        </svg>
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
          <h3>Menu</h3>
          <ul>
            <li>
              <router-link to="/home" class="menu-item">🏠 For you</router-link>
            </li>
            <li>
              <router-link to="/subscriptions" class="menu-item">👤 Subscription</router-link>
            </li>
            <li>
              <router-link to="/discover" class="menu-item">🧭 Discover</router-link>
            </li>
          </ul>
        </nav>
          <div class="subscribed-list">
            <h3>Subscribed accounts</h3>
            <ul>
              <li v-for="account in subscribedAccounts" :key="account.id">
                <!-- ZIDNA HNA ROUTER-LINK -->
                <router-link :to="{ name: 'UserProfile', params: { id: account.id } }" class="user-link">
                  <img :src="account.img" alt="avatar" class="avatar">
                  <span>{{ account.name }}</span>
                </router-link>
              </li>
            </ul>
            <p class="show-more">show more  </p>
          </div>
      </aside>

      <main class="feed-container">
        <p v-if="!feedLoading && videos.length === 0" class="glass-panel empty-feed">
          No videos yet. Owners will publish their events here.
        </p>

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
              {{ activeEvent.owner.is_following ? 'Subscribed' : 'Subscribe' }}
            </button>
          </div>
          <p class="description">{{ activeEvent.description }}</p>
        </div>
        <div class="action-buttons glass-panel">
          <button :class="{ liked: activeEvent.is_liked }" @click="toggleLike">
            {{ activeEvent.is_liked ? '❤️' : '🤍' }} {{ formatCount(activeEvent.likes_count) }}
          </button>
          <button>💬 {{ formatCount(activeEvent.comments_count) }}</button>
          <button>•••</button>
        </div>
        <div class="comments-section glass-panel">
          <h3>Comments</h3>

          <!-- Scrollable list: newest comment is at the bottom, right above the input -->
          <div class="comments-list" ref="commentsListRef">
            <p v-if="comments.length === 0" class="no-comments">No comments yet. Be the first!</p>

            <div class="comment-thread" v-for="comment in comments" :key="comment.id">
              <div class="comment">
                <img :src="comment.user_avatar" alt="avatar" class="avatar comment-avatar">
                <div class="comment-body">
                  <p class="comment-line"><strong>{{ comment.user_username }}</strong> {{ comment.content }}</p>
                  <div class="comment-meta">
                    <span>{{ timeAgo(comment.created_at) }}</span>
                    <button class="reply-btn" @click="startReply(comment, comment)">Reply</button>
                  </div>

                  <button
                    v-if="comment.reply_count > 0"
                    class="view-replies-btn"
                    @click="toggleReplies(comment.id)">
                    <span class="replies-line"></span>
                    {{ expandedReplies[comment.id] ? 'Hide replies' : `View ${comment.reply_count} ${comment.reply_count === 1 ? 'reply' : 'replies'}` }}
                  </button>

                  <div v-if="expandedReplies[comment.id]" class="replies">
                    <div class="comment reply" v-for="reply in comment.replies" :key="reply.id">
                      <img :src="reply.user_avatar" alt="avatar" class="avatar reply-avatar">
                      <div class="comment-body">
                        <p class="comment-line"><strong>{{ reply.user_username }}</strong> {{ reply.content }}</p>
                        <div class="comment-meta">
                          <span>{{ timeAgo(reply.created_at) }}</span>
                          <button class="reply-btn" @click="startReply(reply, comment)">Reply</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Input pinned at the bottom -->
          <div class="comment-composer">
            <div v-if="replyingTo" class="replying-bar">
              <span>Replying to <strong>@{{ replyingTo.username }}</strong></span>
              <button class="cancel-reply" @click="cancelReply" aria-label="Cancel reply">✕</button>
            </div>
            <div class="add-comment-area">
              <input
                ref="commentInputRef"
                type="text"
                v-model="newCommentText"
                :placeholder="replyingTo ? 'Write a reply...' : 'Add a comment...'"
                @keyup.enter="postComment"
                class="comment-input"
              />
              <button @click="postComment" class="send-comment-btn" :disabled="isSending || !newCommentText.trim()">Post</button>
            </div>
          </div>
        </div>
        </template>
      </aside>
    </div>
  </div>
</template>

<style scoped>
/* Il tuo stile CSS rimane esattamente lo stesso */
.feed-video { width: 100%; height: 100%; object-fit: cover; border-radius: 15px; position: absolute; top: 0; left: 0; z-index: 0; }
.video-overlay, .video-controls { position: relative; z-index: 1; }
.video-overlay { position: absolute; bottom: 30px; left: 20px; color: white; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); }
#bgVideo { position: fixed; top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; z-index: -1; object-fit: cover; }
.app-container { display: flex; flex-direction: column; height: 100vh; color: #FFFFFF; font-family: sans-serif; padding: 10px 20px; box-sizing: border-box; }
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
.comment-meta { display: flex; gap: 12px; align-items: center; margin-top: 3px; font-size: 12px; color: rgba(255,255,255,0.6); }
.reply-btn, .view-replies-btn, .cancel-reply { background: none; border: none; color: rgba(255,255,255,0.6); cursor: pointer; font-size: 12px; font-weight: bold; padding: 0; }
.reply-btn:hover, .view-replies-btn:hover { color: #00f2fe; }
.view-replies-btn { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
.replies-line { display: inline-block; width: 24px; height: 1px; background: rgba(255,255,255,0.4); }
.replies { margin-top: 10px; }
.replies .comment { margin-bottom: 10px; font-size: 13px; }
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
</style>
