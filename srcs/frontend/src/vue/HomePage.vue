<script setup>
// 1. ADDED: onMounted import
import { ref, onMounted } from 'vue';

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

// (Mock Data for the Video Feed)
const videos = ref([
  { id: 1, title: 'Video 1: Awesome DJ Set', url: '/videos/video1.mp4' },
  { id: 2, title: 'Video 2: Crazy Crowd', url: '/videos/video2.mp4' }
]);
//#########
const comments = ref([]);
const newCommentText = ref('');
const activeEventId = ref(1);
// 2. ADDED: Array to hold all video elements
const videoRefs = ref([]);

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
const API = 'http://localhost:8000/api';
// GET: Recupera i commenti
const fetchComments = async (eventId) => {
  const token = getToken();
  try {
    const response = await fetch(`${API}/social/events/${eventId}/comments/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
      comments.value = await response.json();
    }
  } catch (error) {
    console.error('Errore durante il recupero dei commenti:', error);
  }
};

// POST: Salva il nuovo commento
const postComment = async () => {
  if (!newCommentText.value.trim()) return;
  const token = getToken();

  try {
    const response = await fetch(`${API}/social/events/${activeEventId.value}/comments/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ content: newCommentText.value })
    });

    if (response.ok) {
      const addedComment = await response.json();
      comments.value.unshift(addedComment); // Inserisce il commento in cima alla lista
      newCommentText.value = ''; // Svuota la casella di testo
    } else {
        alert("Errore nel salvataggio del commento.");
    }
  } catch (error) {
    console.error('Errore di rete durante l\'invio del commento:', error);
  }
};
// Intersection Observer (The Radar)
onMounted(() => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.play();
      } else {
        entry.target.pause();
      }
    });
  }, {
    threshold: 0.6
  });

  videoRefs.value.forEach((videoEl) => {
    if (videoEl) {
      observer.observe(videoEl);
    }
  });
  fetchComments(activeEventId.value);
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
        <div class="video-wrapper glass-panel" v-for="(video, index) in videos" :key="video.id">
          <video
            :ref="el => { if (el) videoRefs[index] = el }"
            class="feed-video"
            :src="video.url"
            loop
            :muted="isMuted"
            playsinline
            @click="togglePlay">
          </video>
          <div class="video-overlay">
            <h2>{{ video.title }}</h2>
          </div>
          <div class="video-controls">
            <!-- <div class="volume-slider">|</div> -->
            <button class="volume-btn" @click="toggleMute">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="video-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z" />
              </svg>
            </button>
          </div>
        </div>
      </main>

      <aside class="right-sidebar">
        <div class="owner-info glass-panel">
          <div class="owner-header">
            <img src="https://i.pravatar.cc/150?u=4" alt="owner" class="avatar">
            <div>
              <p class="owner-name">local owner ✔</p>
              <p class="owner-handle">@club1 · 2h ago</p>
            </div>
            <button class="subscribe-btn">Subscribe</button>
          </div>
          <p class="description">Florence was on fire last night! Incredible sets... #nightlife #party</p>
        </div>
        <div class="action-buttons glass-panel">
          <button>❤️ 3.1k</button>
          <button>🔖 2.2k</button>
          <button>•••</button>
        </div>
            <div class="comments-section glass-panel">
      <h3>Comments</h3>

      <!-- Sezione input del commento -->
      <div class="add-comment-area">
        <input
          type="text"
          v-model="newCommentText"
          placeholder="Scrivi un commento..."
          @keyup.enter="postComment"
          class="comment-input"
        />
        <button @click="postComment" class="send-comment-btn">Invia</button>
      </div>

      <!-- Render dei commenti reali -->
          <div class="comment" v-for="comment in comments" :key="comment.id">
            <img :src="comment.user_avatar" alt="avatar" class="avatar">
            <div class="comment-text">
              <!-- Mostriamo l'username dell'autore e il testo vero -->
              <strong>{{ comment.user_username }}</strong>
              <p>{{ comment.content }}</p>
            </div>
          </div>
        </div>
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
.navbar { display: flex; justify-content: space-between; align-items: center; height: 60px; margin-bottom: 15px; flex-shrink: 0; }
.search-bar input { background: rgba(255, 255, 255, 0.1); border: none; border-radius: 17px; padding: 10px 20px; color: white; width: 300px; }
.main-content { display: flex; flex-direction: row; justify-content: space-between; width: 100%; height: calc(100vh - 95px); overflow: hidden; }
.left-sidebar { width: 280px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
.right-sidebar { width: 320px; display: flex; flex-direction: column; gap: 15px; overflow-y: auto; }
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
.comment { display: flex; gap: 10px; margin-bottom: 15px; font-size: 14px; }
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

.add-comment-area {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
.comment-input {
  flex-grow: 1;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 17px;
  padding: 8px 15px;
  color: white;
}
.send-comment-btn {
  background: #00f2fe;
  color: #000;
  border: none;
  border-radius: 10px;
  padding: 8px 15px;
  font-weight: bold;
  cursor: pointer;
}
</style>
