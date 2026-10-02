<script setup>
import { ref } from 'vue';

// Use your existing mock data for the sidebar here
const subscribedAccounts = ref([
  { id: 1, name: 'Xhul', img: 'https://i.pravatar.cc/150?u=1' },
  { id: 2, name: 'Anna', img: 'https://i.pravatar.cc/150?u=2' }
]);

const subFeed = ref([
  { id: 1, user: 'Anna', title: 'Weekend vibes', likes: '5.2k' },
  { id: 2, user: 'Xhul', title: 'New track out now', likes: '1.8k' }
]);
</script>

<template>
  <video autoplay muted loop playsinline id="bgVideo">
      <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
  </video>

  <div class="app-container">
    <!-- Paste your standard Navbar here -->

    <div class="main-content">
      <!-- Paste your standard Left Sidebar (with router-links) here -->

      <!-- Center: Subscriptions Feed -->
      <main class="feed-container glass-panel">
        <h2>Subscriptions Feed</h2>
        <div class="video-scroll-area">
          <div v-for="video in subFeed" :key="video.id" class="feed-video-card">
            <div class="video-placeholder">Video by {{ video.user }}</div>
            <div class="video-info">
              <h3>{{ video.title }}</h3>
              <span>❤️ {{ video.likes }}</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Paste your standard layout styles here (app-container, glass-panel, navbar, sidebar) */

.feed-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
.video-scroll-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
  padding-top: 20px;
}
.feed-video-card {
  width: 100%;
  max-width: 400px;
  aspect-ratio: 9/16;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 15px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}
.video-info {
  position: absolute;
  bottom: 20px;
  left: 20px;
}
</style>
