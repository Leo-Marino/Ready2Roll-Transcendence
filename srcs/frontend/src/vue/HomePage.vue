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
const comments = ref([
  { id: 1, user: 'Xhul', text: 'The drop on that first track was insanity!' },
  { id: 2, user: 'Anna', text: 'Best set of the year so far!' }
]);

// (Mock Data for the Video Feed)
const videos = ref([
  { id: 1, title: 'Video 1: Awesome DJ Set', url: '/videos/video1.mp4' },
  { id: 2, title: 'Video 2: Crazy Crowd', url: '/videos/video2.mp4' }
]);

// 2. ADDED: Array to hold all video elements (This caused the white screen!)
const videoRefs = ref([]);

// Controls global mute state
const isMuted = ref(true);

// Function to play or pause the video when clicked
const togglePlay = (event) => {
  const videoElement = event.target;
  if (videoElement.paused) {
    videoElement.play();
  } else {
    videoElement.pause();
  }
};

// Intersection Observer (The Radar)
onMounted(() => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      // If the video comes into view (at least 60% visible)
      if (entry.isIntersecting) {
        entry.target.play(); // Play the video automatically
      } else {
        // If the video leaves the screen, pause it immediately
        entry.target.pause();
      }
    });
  }, {
    threshold: 0.6 // Trigger when 60% of the video is visible
  });

  // Attach the observer to all video elements
  videoRefs.value.forEach((videoEl) => {
    if (videoEl) {
      observer.observe(videoEl);
    }
  });
});
</script>

<template>
  <!-- Background Video -->
  <video autoplay muted loop playsinline id="bgVideo">
      <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
  </video>

  <div class="app-container">

    <!-- Top Navbar -->
    <header class="navbar glass-panel">
      <div class="logo">
        <span style="color: #00f2fe; font-weight: bold;">R</span> Ready2Roll
      </div>
      <div class="search-bar">
        <input type="text" placeholder="Search...">
      </div>
      <div class="nav-icons">
        <span>✈️</span>
        <span>💬</span>
      </div>
    </header>

    <div class="main-content">

      <!-- 1. Left Sidebar -->
      <aside class="left-sidebar glass-panel">
        <nav class="main-menu">
          <h3>Menu</h3>
          <ul>
            <li>🏠 For you</li>
            <li>👤 Subscription</li>
            <li>🧭 Discover</li>
          </ul>
        </nav>

        <div class="subscribed-list">
          <h3>Subscribed accounts</h3>
          <ul>
            <li v-for="account in subscribedAccounts" :key="account.id">
              <img :src="account.img" alt="avatar" class="avatar">
              <span>{{ account.name }}</span>
            </li>
          </ul>
          <p class="show-more">show more ⌄</p>
        </div>
      </aside>
<!-- 2. Center (Main Video Feed) -->
      <main class="feed-container">

        <!-- NEW: Added 'index' to the v-for loop -->
        <div class="video-wrapper glass-panel" v-for="(video, index) in videos" :key="video.id">

          <!-- NEW: Changed how 'ref' pushes elements into the array in Vue 3 -->
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
            <button>ᐱ</button>
            <button>ᐯ</button>
            <div class="volume-slider">|</div>
            <button @click="isMuted = !isMuted">
              {{ isMuted ? '🔇' : '🔊' }}
            </button>
          </div>

        </div>

      </main>
      <!-- 3. Right Sidebar -->
      <aside class="right-sidebar">

        <!-- Video Owner Information -->
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

        <!-- Action Buttons (Like, Bookmark, Options) -->
        <div class="action-buttons glass-panel">
          <button>❤️ 3.1k</button>
          <button>🔖 2.2k</button>
          <button>•••</button>
        </div>

        <!-- Comments Section -->
        <div class="comments-section glass-panel">
          <h3>Comments</h3>
          <div class="comment" v-for="comment in comments" :key="comment.id">
            <img :src="'https://i.pravatar.cc/150?u=' + comment.id" alt="avatar" class="avatar">
            <div class="comment-text">
              <strong>{{ comment.user }}</strong>
              <p>{{ comment.text }}</p>
            </div>
          </div>
        </div>
      </aside>

    </div>
  </div>
</template>

<style scoped>
/* Styling the actual video tag */
.feed-video {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Ensures the video fills the box without stretching */
  border-radius: 15px;
  position: absolute; /* Places the video behind the text and buttons */
  top: 0;
  left: 0;
  z-index: 0;
}

/* Ensure text and buttons stay above the video */
.video-overlay, .video-controls {
  position: relative;
  z-index: 1;
}

/* Styling the video title overlay */
.video-overlay {
  position: absolute;
  bottom: 30px;
  left: 20px;
  color: white;
  text-shadow: 1px 1px 4px rgba(0,0,0,0.8); /* Makes text readable over bright videos */
}
#bgVideo {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    object-fit: cover;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  color: #FFFFFF;
  font-family: sans-serif;
  padding: 10px 20px; /* Added side padding for better framing */
  box-sizing: border-box;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 15px;
  box-sizing: border-box;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  margin-bottom: 15px;
  flex-shrink: 0;
}

.search-bar input {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 17px;
  padding: 10px 20px;
  color: white;
  width: 300px;
}

.main-content {
  display: flex;
  flex-direction: row;
  justify-content: space-between; /* Pushes items to the far left and right */
  width: 100%;
  height: calc(100vh - 95px);
  overflow: hidden;
}

/* Sidebar sizing */
.left-sidebar {
  width: 280px; /* Adjusted width for balance */
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.right-sidebar {
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  overflow-y: auto;
}
/*
  TikTok-style Smooth Scrolling Logic
*/
/* Container for the video feed */
.feed-container {
  flex-grow: 1;
  max-width: 550px;
  height: 100%;
  overflow-y: scroll;

  /* The magic for snapping */
  scroll-snap-type: y mandatory;

  /* 1. Add this to make the scrolling movement smooth instead of instant */
  scroll-behavior: smooth;

  scrollbar-width: none;
  display: flex;
  flex-direction: column;
}

/* Individual video container */
.video-wrapper {
  min-height: 100%;
  width: 100%;

  /* Snaps to the start of the video */
  scroll-snap-align: start;

  /* 2. Add this! It forces the scroll to STOP at every single video (feels heavier/controlled) */
  scroll-snap-stop: always;

  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 15px;
  margin-bottom: 15px;
}

/* Styling for video placeholder content */
.video-placeholder {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
}

.video-controls {
  position: absolute;
  right: 15px;
  bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.video-controls button {
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  cursor: pointer;
}

/*
  General UI Components Styling
*/
ul {
  list-style: none;
  padding: 0;
}
li {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  cursor: pointer;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.subscribe-btn {
  background: rgba(0, 242, 254, 0.7);
  color: white;
  border: none;
  border-radius: 10px;
  padding: 8px 15px;
  cursor: pointer;
  font-weight: bold;
}
.owner-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.action-buttons {
  display: flex;
  justify-content: space-around;
}
.action-buttons button {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  padding: 10px;
  border-radius: 10px;
  cursor: pointer;
}

.comment {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  font-size: 14px;
}
</style>
