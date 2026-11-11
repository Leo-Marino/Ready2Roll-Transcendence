<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import EventMediaGrid from './EventMediaGrid.vue';
import SearchBar from './SearchBar.vue';
import LanguageSwitcher from './LanguageSwitcher.vue';
import { t as $t } from '../i18n';
import { useSocialSocket } from '../composables/useSocialSocket';
import NotificationBell from './NotificationBell.vue';
import ChatNavLink from './ChatNavLink.vue';

const route = useRoute();
const router = useRouter();
const API = '/api';

const getToken = () =>
  localStorage.getItem('token') ||
  localStorage.getItem('access') ||
  localStorage.getItem('access_token');

const DEFAULT_AVATAR = 'https://i.pravatar.cc/150?u=6';

const userProfile = ref({
  name: '',
  following: 0,
  followers: 0,
  description: '',
  avatar: DEFAULT_AVATAR,
  isOnline: false,
});

const isBusiness = ref(false);
const userEvents = ref([]);
const isFollowing = ref(false);
const isSelf = ref(false);
const followLoading = ref(false);
const errorMessage = ref('');

const fetchUserProfile = async (userId) => {
  const token = getToken();
  if (!token) {
    router.push('/login');
    return;
  }

  errorMessage.value = '';

  try {
    const response = await fetch(`${API}/users/${userId}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 401) {
      router.push('/login');
      return;
    }
    if (response.status === 404) {
      errorMessage.value = 'User not found';
      return;
    }
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    userProfile.value.name = data.username || '';
    userProfile.value.description = data.bio || '';
    userProfile.value.avatar = data.avatar_url || DEFAULT_AVATAR;
    userProfile.value.following = data.following_count || 0;
    userProfile.value.followers = data.followers_count || 0;
    userProfile.value.isOnline = !!data.is_online;
    isFollowing.value = !!data.is_following;
    isSelf.value = !!data.is_self;
    isBusiness.value = data.type_of_user === 'business';
    fetchUserEvents(userId);
  } catch (error) {
    errorMessage.value = 'Could not load this profile.';
  }
};

const fetchUserEvents = async (userId) => {
  userEvents.value = [];
  try {
    const response = await fetch(`${API}/users/${userId}/events/`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (response.ok) userEvents.value = await response.json();
  } catch (error) {
    console.error('Error loading events:', error);
  }
};

// --- Live updates from other users (WebSocket) ---
// isFollowing is personal state and is only changed by my own click;
// here we only update the public counters.
const handleSocialMessage = (message) => {
  const { action, target_id: targetId, data } = message;

  if (action === 'follow') {
    if (targetId === Number(route.params.id)) {
      userProfile.value.followers = data.followers_count;
      userProfile.value.following = data.following_count;
    }
  } else if (action === 'like' || action === 'comment') {
    userEvents.value.forEach((ev) => {
      if (ev.id !== targetId) return;
      if (action === 'like') ev.likes_count = data.likes_count;
      else ev.comments_count = data.comments_count;
    });
} else if (action === 'update_profile') {
    // ---> BULLETPROOF LIVE PROFILE UPDATES <---
    if (targetId === Number(route.params.id)) {
      // Check all possible backend key names, fallback to existing name if missing
      userProfile.value.name = data.username || data['user.name'] || data.name || userProfile.value.name;

      // Same for bio
      userProfile.value.description = data.user_bio || data.bio || userProfile.value.description;

      // Same for avatar
      const newAvatar = data.user_avatar || data.avatar_url || data.avatar;
      if (newAvatar) {
         userProfile.value.avatar = newAvatar;
      }
    }
  } else if (action === 'online_status') {
    if (targetId === Number(route.params.id)) {
      userProfile.value.isOnline = !!data.is_online;
    }
  } else if (action === 'resync') {
    fetchUserProfile(route.params.id);
    fetchUserEvents(route.params.id);
  }
};

useSocialSocket(handleSocialMessage);

// Prima volta che la pagina si carica
onMounted(() => {
  fetchUserProfile(route.params.id);
});

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchUserProfile(newId);
  }
});

const toggleFollow = async () => {
  const token = getToken();
  if (!token) {
    router.push('/login');
    return;
  }
  if (followLoading.value) return;

  followLoading.value = true;
  try {
    const response = await fetch(`${API}/social/follow/${route.params.id}/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    isFollowing.value = data.is_following;
    userProfile.value.followers = data.followers_count;
  } catch (error) {
    alert('Could not update follow status.');
  } finally {
    followLoading.value = false;
  }
};
</script>

<template>
  <video autoplay muted loop playsinline id="bgVideo">
    <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
  </video>

    <div class="app-container">
        <header class="navbar glass-panel">
          <div class="logo" @click="$router.push('/home')">
            <img src="../assets/logo_temp.png" alt="Ready2Roll Logo" class="nav-logo-img">
            <span class="logo-text">Ready2Roll</span>
          </div>

          <SearchBar />

          <div class="nav-icons">
            <LanguageSwitcher />

            <router-link to="/chat" class="nav-icon-link">
              <ChatNavLink>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                </svg>
              </ChatNavLink>
            </router-link>

            <NotificationBell />

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
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="menu-svg-icon">
                <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/>
                <path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              </svg>
              <span>{{ $t('forYou') }}</span>
            </li>
            <li @click="$router.push('/subscriptions')" class="menu-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="menu-svg-icon">
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
                <path d="M12 3l0 2" /><path d="M12 19l0 2" /><path d="M3 12l2 0" /><path d="M19 12l2 0" />
              </svg>
              <span>{{ $t('discover') }}</span>
            </li>
          </ul>
        </nav>
      </aside>

      <main class="profile-container">
        <p v-if="errorMessage" class="glass-panel error-msg">{{ errorMessage }}</p>
        <div v-else class="profile-header glass-panel">
          <img :src="userProfile.avatar" alt="Profile Avatar" class="profile-avatar">
          <div class="profile-info">
            <div class="name-row">
              <h2>
                {{ userProfile.name }}
                <svg v-if="isBusiness" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="#00f2fe" stroke="#00f2fe" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="verified-badge" title="Business Account">
                  <path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"/>
                  <path d="m16 9-5.5 5.5L8 12" stroke="#ffffff" stroke-width="2.5"/>
                </svg>
                <span class="status-pill" :class="{ online: userProfile.isOnline }">
                  <span class="status-dot"></span>
                  {{ userProfile.isOnline ? $t('rollyStatusOnline') : 'offline' }}
                </span>
              </h2>
            </div>
            <div class="stats-row">
              <span class="clickable-stat">
                <strong>{{ userProfile.following }}</strong> {{ $t('following') }}
              </span>
              <span class="clickable-stat">
                <strong>{{ userProfile.followers }}</strong> {{ $t('followers') }}
              </span>
            </div>
            <div class="description-box">
              <p>{{ userProfile.description || $t('noBio') }}</p>
            </div>
          </div>

          <div class="action-buttons">
            <button v-if="isSelf" class="follow-btn" @click="$router.push('/profile')">
              {{ $t('editProfile') }}
            </button>
            <button
              v-else
              :class="isFollowing ? 'unfollow-btn' : 'follow-btn'"
              :disabled="followLoading"
              @click="toggleFollow"
            >
              {{ isFollowing ? $t('unfollow') : $t('follow') }}
            </button>
          </div>
        </div>

        <template v-if="!errorMessage && isBusiness">
          <div class="profile-tabs glass-panel">
            <div class="tab active"><span>{{ $t('videos') }}</span></div>
          </div>
          <EventMediaGrid :events="userEvents" :empty-text="$t('noBusinessVideos')" />
        </template>
      </main>
    </div>
  </div>
</template>

<style scoped>
#bgVideo { position: fixed; top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; z-index: -1; object-fit: cover; }
.app-container { display: flex; flex-direction: column; height: 100vh; color: #FFFFFF; font-family: var(--font-main); padding: 10px 20px; box-sizing: border-box; }
.glass-panel { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; box-sizing: border-box; }
.navbar { display: flex; justify-content: space-between; align-items: center; height: 60px; margin-bottom: 15px; flex-shrink: 0; }
.logo { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.nav-logo-img { height: 35px; width: auto; object-fit: contain; }
.logo-text { font-family: "Bruno Ace", sans-serif; font-weight: bold; font-size: 1.2rem; }
.nav-icons { display: flex; gap: 20px; align-items: center; }
.nav-icon { width: 26px; height: 26px; color: #FFFFFF; cursor: pointer; transition: all 0.3s ease; }
.nav-icon:hover { color: #00f2fe; transform: scale(1.15); }
.nav-icon-link { display: flex; align-items: center; }

.main-content { display: flex; flex-direction: row; gap: 20px; height: calc(100vh - 95px); width: 100%; }
.left-sidebar { width: 280px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
ul { list-style: none; padding: 0; }
li { display: flex; align-items: center; gap: 10px; margin-bottom: 15px; cursor: pointer; }

.profile-container { flex-grow: 1; display: flex; flex-direction: column; gap: 15px; overflow-y: auto; scrollbar-width: none; }
.profile-container::-webkit-scrollbar { display: none; }
.profile-header { display: flex; align-items: flex-start; gap: 30px; position: relative; }
.profile-avatar { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; }
.profile-info { display: flex; flex-direction: column; gap: 10px; flex-grow: 1; }
.name-row h2 { margin: 0; display: flex; align-items: center; gap: 8px; }
.stats-row { display: flex; gap: 20px; font-size: 1rem; }
.description-box { background: rgba(255, 255, 255, 0.05); padding: 10px 15px; border-radius: 10px; min-height: 50px; width: 60%; border: 1px solid rgba(255, 255, 255, 0.2); }

.profile-tabs { display: flex; justify-content: center; padding: 10px; border-radius: 10px; }
.tab { padding: 10px 40px; font-weight: bold; cursor: pointer; border-bottom: 2px solid #00f2fe; color: white; }

.action-buttons { position: absolute; bottom: 20px; right: 20px; display: flex; gap: 10px; }
.follow-btn { background: #00f2fe; color: #000; border: none; border-radius: 10px; padding: 10px 30px; font-weight: bold; cursor: pointer; transition: background 0.3s; }
.follow-btn:hover { background: #05d4ca; }
.unfollow-btn { background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.5); border-radius: 10px; padding: 10px 30px; font-weight: bold; cursor: pointer; transition: background 0.3s; }
.unfollow-btn:hover { background: rgba(255, 71, 87, 0.8); border-color: transparent; }
.error-msg { text-align: center; font-weight: bold; }
.follow-btn:disabled, .unfollow-btn:disabled { opacity: 0.6; cursor: wait; }
.clickable-stat { cursor: default; }

.main-menu h3 { margin-bottom: 20px; color: rgba(255, 255, 255, 0.8); }
.main-menu ul { display: flex; flex-direction: column; gap: 15px; }
.menu-item { display: flex; align-items: center; gap: 12px; cursor: pointer; transition: all 0.2s ease; font-size: 1.05rem; }
.menu-svg-icon { width: 22px; height: 22px; color: rgba(255, 255, 255, 0.7); transition: color 0.2s ease, transform 0.2s ease; }
.menu-item:hover .menu-svg-icon, .menu-item:hover { color: #00f2fe; transform: scale(1.02); }

/* RTL Fixes for Profile Buttons */
[dir="rtl"] .profile-header {
  padding-bottom: 70px; /* Zidna l'espace lta7t bach maytla3ch l'button fo9 l'bio */
}

[dir="rtl"] .action-buttons-styled {
  right: auto;
  left: 20px;
  bottom: 20px;
  flex-direction: row-reverse;
}

@media (max-width: 768px) {
  [dir="rtl"] .action-buttons-styled {
    position: static;
    margin-top: 15px;
    justify-content: center;
  }
  [dir="rtl"] .profile-header {
    padding-bottom: 20px;
  }
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.status-pill.online {
  background: rgba(61, 255, 160, 0.14);
  border-color: rgba(61, 255, 160, 0.5);
  color: #3dffa0;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
}
.status-pill.online .status-dot {
  background: #3dffa0;
  box-shadow: 0 0 8px #3dffa0;
}

</style>
