<script setup>
import { ref } from 'vue';

// (Mock Data)
const subscribedAccounts = ref([
  { id: 1, name: 'Xhul', img: 'https://i.pravatar.cc/150?u=1' },
  { id: 2, name: 'Anna', img: 'https://i.pravatar.cc/150?u=2' },
  { id: 3, name: 'thilina', img: 'https://i.pravatar.cc/150?u=3' }
]);

const comments = ref([
  { id: 1, user: 'Xhul', text: 'The drop on that first track was insanity!' },
  { id: 2, user: 'Anna', text: 'Best set of the year so far!' }
]);
</script>

<template>
  <video autoplay muted loop playsinline id="bgVideo">
      <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
  </video>

  <div class="app-container">

    <!-- Navbar -->
    <header class="navbar glass-panel">
      <div class="logo">
        <!-- Logo section -->
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

      <!-- 2. Center (Main Video Area) -->
      <main class="video-container glass-panel">
        <div class="video-placeholder">
          <!-- The event video will be placed here -->
          <p>The Video</p>
        </div>
        <div class="video-controls">
          <button>ᐱ</button>
          <button>ᐯ</button>
          <div class="volume-slider">|</div>
          <button>🔊</button>
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
/*
  Using the same style from the Signup/Login pages
  to maintain a clean and consistent design
*/
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
  padding: 10px;
  box-sizing: border-box;
}

/* This magic class applies the clean glassmorphism effect */
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
  gap: 20px;
  height: calc(100vh - 90px);
}

/* Layout structure */
.left-sidebar {
  width: 250px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.video-container {
  flex-grow: 1;
  display: flex;
  position: relative;
  justify-content: center;
  align-items: center;
}

.right-sidebar {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* Styling for lists and avatars */
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

/* Buttons styling */
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
