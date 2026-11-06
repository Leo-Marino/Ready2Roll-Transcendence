<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
body, html {
  margin: 0 !important;
  padding: 0 !important;
  width: 100% !important;
  height: 100% !important;
  overflow-x: hidden !important;
}

#app {
  width: 100% !important;
  min-height: 100% !important;
  overflow-x: hidden !important;
}

/* Bach l'ktaba twila b7al saddddddd... matkhrejch 3la l'cadre */
.description-box,
.description-box p {
  word-break: break-word !important;
  overflow-wrap: break-word !important;
}

/* ================================================== */
/* 🌐 RTL (ARABIC) SUPPORT (Ga3 les pages) 🌐 */
/* ================================================== */

/* Fix Navbar in RTL */
[dir="rtl"] .navbar {
  direction: ltr !important;
  flex-direction: row !important;
}

/* Force alignment inside the navbar to avoid squishing in the center */
[dir="rtl"] .navbar .nav-left,
[dir="rtl"] .navbar .nav-right {
  direction: ltr !important;
}

/* Fix Sidebar positioning in RTL (HomePage, Profile, etc.) */
[dir="rtl"] .main-content {
  flex-direction: row-reverse; /* Keep left sidebar on the left */
}

/* Fix text alignment in RTL */
[dir="rtl"] .profile-info,
[dir="rtl"] .stats-row,
[dir="rtl"] .name-row {
  text-align: right;
  align-items: flex-end;
}
[dir="rtl"] .name-row h2 {
  flex-direction: row-reverse; /* Badge on the left of the name */
}

[dir="rtl"] .left-sidebar .menu-item {
   flex-direction: row-reverse;
   justify-content: flex-end;
}

[dir="rtl"] .action-buttons-styled {
   right: auto;
   left: 20px; /* Move buttons to the left side */
   flex-direction: row-reverse;
}

/* ================================================== */
/* 📱 GLOBAL RESPONSIVE DESIGN (Ga3 les pages) 📱 */
/* ================================================== */
@media (max-width: 1024px) {
  .app-container {
    height: auto !important;
    min-height: 100vh !important;
    padding: 10px !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
  }

  /* 1. Navbar */
  .navbar, [dir="rtl"] .navbar {
    width: 100% !important;
    padding: 8px 12px !important;
    gap: 10px !important;
    box-sizing: border-box !important;
    flex-direction: row !important; /* Reset to row on mobile */
  }

  .logo-text {
    display: none !important;
  }

  .nav-icons {
    gap: 12px !important;
  }

  /* 2. Main Content & Sidebars (Home, Profile, Chat) */
  .main-content, [dir="rtl"] .main-content {
    flex-direction: column !important;
    height: auto !important;
    overflow: visible !important;
    gap: 15px !important;
  }

  .left-sidebar {
    display: none !important;
  }

  /* F HomePage: l'partie d comments (right-sidebar) thbet lta7t */
  .right-sidebar {
    width: 100% !important;
    max-width: 100% !important;
    height: auto !important;
  }

  /* 3. Profile Header & Info */
  .profile-container {
    overflow: visible !important;
    width: 100% !important;
  }

  .profile-header, [dir="rtl"] .profile-header {
    flex-direction: column !important;
    align-items: center !important;
    text-align: center !important;
    gap: 15px !important;
    padding: 20px 15px !important;
  }

  .profile-info, [dir="rtl"] .profile-info {
    align-items: center !important;
    width: 100% !important;
    text-align: center !important;
  }

  .name-row,
  .name-row h2,
  .stats-row,
  [dir="rtl"] .name-row,
  [dir="rtl"] .name-row h2,
  [dir="rtl"] .stats-row {
    justify-content: center !important;
  }

  .description-box {
    width: 100% !important;
    box-sizing: border-box !important;
  }

  /* 4. Buttons dyal ProfileView (.action-buttons-styled) o OtherUserProfileView (.action-buttons) */
  .action-buttons,
  .action-buttons-styled,
  [dir="rtl"] .action-buttons-styled {
    position: static !important;
    bottom: auto !important;
    right: auto !important;
    left: auto !important;
    margin-top: 10px !important;
    width: 100% !important;
    justify-content: center !important;
    flex-wrap: wrap !important;
  }

  /* 5. Grids dyal Events, Videos o Users */
  .events-grid,
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)) !important;
    gap: 12px !important;
  }

  .users-grid {
    grid-template-columns: 1fr !important;
  }

  /* 6. Modals (Stats & Edit Profile) */
  .stats-modal-card {
    flex-direction: column !important;
    align-items: center !important;
    max-height: 90vh !important;
    overflow-y: auto !important;
    padding: 15px !important;
  }

  .stats-media-box {
    height: 40vh !important;
    width: auto !important;
  }

  .stats-metrics-grid {
    grid-template-columns: 1fr 1fr !important;
  }
}

@media (max-width: 480px) {
  .profile-tabs .tab {
    padding: 10px 20px !important;
  }

  .action-pill {
    padding: 8px 12px !important;
    font-size: 0.78rem !important;
  }

  .stats-metrics-grid {
    grid-template-columns: 1fr !important;
  }
}
</style>
