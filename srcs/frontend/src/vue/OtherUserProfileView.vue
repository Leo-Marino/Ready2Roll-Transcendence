<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import EventMediaGrid from './EventMediaGrid.vue';

const route = useRoute();
const router = useRouter();
const API = '/api';

const getToken = () =>
  localStorage.getItem('token') ||
  localStorage.getItem('access') ||
  localStorage.getItem('access_token');


const likedVideos = ref([
  { id: 1, title: 'Video 1', thumbnail: '' },
  { id: 2, title: 'Video 2', thumbnail: '' },
]);

const DEFAULT_AVATAR = 'https://i.pravatar.cc/150?u=6';

const userProfile = ref({
  name: '',
  following: 0,
  followers: 0,
  description: '',
  avatar: DEFAULT_AVATAR,
});

const isBusiness = ref(false);
const userEvents = ref([]);
const isFollowing = ref(false);
const isSelf = ref(false);
const followLoading = ref(false);
const errorMessage = ref('');

// GET /api/users/<id>/
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
    userProfile.value.avatar = data.avatar_url || DEFAULT_AVATAR;   // URL gia' completo dal backend
    userProfile.value.following = data.following_count || 0;
    userProfile.value.followers = data.followers_count || 0;
    isFollowing.value = !!data.is_following;
    isSelf.value = !!data.is_self;
    isBusiness.value = data.type_of_user === 'business';
    fetchUserEvents(userId);
  } catch (error) {
    console.error('Error loading profile:', error);
    errorMessage.value = 'Could not load this profile.';
  }
};

// GET /api/users/<id>/events/  -> videos created by this owner
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

// Prima volta che la pagina si carica
onMounted(() => {
  fetchUserProfile(route.params.id);
});

// Se cambia l'ID nell'URL (stesso componente riutilizzato), ricarica i dati
watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchUserProfile(newId);
  }
});

// POST /api/social/follow/<id>/  (toggle follow / unfollow)
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

    // Il backend e' la fonte di verita': uso lo stato che mi ritorna
    const data = await response.json();
    isFollowing.value = data.is_following;
    userProfile.value.followers = data.followers_count;
  } catch (error) {
    console.error('Error toggling follow:', error);
    alert('Could not update follow status. Please try again.');
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
      <div class="search-bar">
        <input type="text" placeholder="search">
      </div>
      <div class="nav-icons">
        <router-link to="/chat" class="nav-icon-link">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" /></svg>
        </router-link>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 011.037-.443 48.282 48.282 0 005.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" /></svg>
        <router-link to="/profile" class="nav-icon-link">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>
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
      </aside>

      <main class="profile-container">
        <p v-if="errorMessage" class="glass-panel error-msg">{{ errorMessage }}</p>
        <div v-else class="profile-header glass-panel">
          <img :src="userProfile.avatar" alt="Profile Avatar" class="profile-avatar">
          <div class="profile-info">
            <div class="name-row">
              <h2>{{ userProfile.name }}</h2>
            </div>
            <div class="stats-row">
              <span class="clickable-stat">
                <strong>{{ userProfile.following }}</strong> following
              </span>
              <span class="clickable-stat">
                <strong>{{ userProfile.followers }}</strong> followers
              </span>
            </div>
            <div class="description-box">
              <p>{{ userProfile.description }}</p>
            </div>
          </div>

          <div class="action-buttons">
            <button
                v-if="isSelf"
                class="follow-btn"
                @click="$router.push('/profile')"
            >
                Edit profile
            </button>
            <button
                v-else
                :class="isFollowing ? 'unfollow-btn' : 'follow-btn'"
                :disabled="followLoading"
                @click="toggleFollow"
            >
                {{ isFollowing ? 'Unfollow' : 'Follow' }}
            </button>
          </div>
        </div>

        <template v-if="!errorMessage && isBusiness">
          <div class="profile-tabs glass-panel">
            <div class="tab active"><span>🎬 Videos</span></div>
          </div>
          <EventMediaGrid :events="userEvents" empty-text="This business hasn't posted any videos yet." />
        </template>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Core layout styles */
#bgVideo { position: fixed; top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; z-index: -1; object-fit: cover; }
.app-container { display: flex; flex-direction: column; height: 100vh; color: #FFFFFF; font-family: sans-serif; padding: 10px 20px; box-sizing: border-box; }
.glass-panel { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; box-sizing: border-box; }
.navbar { display: flex; justify-content: space-between; align-items: center; height: 60px; margin-bottom: 15px; flex-shrink: 0; }
.logo { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.nav-logo-img { height: 35px; width: auto; object-fit: contain; }
.logo-text { font-family: "Bruno Ace", sans-serif; font-weight: bold; font-size: 1.2rem; }
.search-bar input { background: rgba(255, 255, 255, 0.1); border: none; border-radius: 17px; padding: 10px 20px; color: white; width: 300px; }
.nav-icons { display: flex; gap: 20px; align-items: center; }
.nav-icon { width: 26px; height: 26px; color: #FFFFFF; cursor: pointer; transition: all 0.3s ease; }
.nav-icon:hover { color: #00f2fe; transform: scale(1.15); }
.nav-icon-link { display: flex; align-items: center; }

.main-content { display: flex; flex-direction: row; gap: 20px; height: calc(100vh - 95px); width: 100%; }
.left-sidebar { width: 250px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
ul { list-style: none; padding: 0; }
li { display: flex; align-items: center; gap: 10px; margin-bottom: 15px; cursor: pointer; }

/* Zidna had style l router-link bach tban bhal li knt */
.user-link {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: white;
  width: 100%;
  transition: color 0.3s ease;
}
.user-link:hover { color: #00f2fe; }

.avatar { width: 40px; height: 40px; border-radius: 50%; }
.show-more { color: #cccccc; cursor: pointer; font-size: 0.9rem; }

.profile-container { flex-grow: 1; display: flex; flex-direction: column; gap: 15px; overflow-y: auto; scrollbar-width: none; }
.profile-container::-webkit-scrollbar { display: none; }
.profile-header { display: flex; align-items: flex-start; gap: 30px; position: relative; }
.profile-avatar { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; }
.profile-info { display: flex; flex-direction: column; gap: 10px; flex-grow: 1; }
.name-row h2 { margin: 0; display: flex; align-items: center; gap: 5px; }
.stats-row { display: flex; gap: 20px; font-size: 1rem; }
.description-box { background: rgba(255, 255, 255, 0.05); padding: 10px 15px; border-radius: 10px; min-height: 50px; width: 60%; border: 1px solid rgba(255, 255, 255, 0.2); }

.profile-tabs { display: flex; justify-content: center; padding: 10px; border-radius: 10px; }
.tab { padding: 10px 40px; font-weight: bold; cursor: pointer; border-bottom: 2px solid #00f2fe; color: white; }

.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
.video-card { aspect-ratio: 9 / 16; display: flex; justify-content: center; align-items: center; position: relative; cursor: pointer; transition: transform 0.2s; }
.video-card:hover { transform: scale(1.02); }
.placeholder-text { font-family: "Bruno Ace", sans-serif; font-size: 1.5rem; opacity: 0.5; }
.heart-icon { position: absolute; bottom: 15px; right: 15px; font-size: 1.5rem; }

.action-buttons {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
}

/* Follow Button Styles */
.follow-btn {
  background: #00f2fe;
  color: #000;
  border: none;
  border-radius: 10px;
  padding: 10px 30px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}
.follow-btn:hover { background: #05d4ca; }

.unfollow-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  padding: 10px 30px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}
.unfollow-btn:hover { background: rgba(255, 71, 87, 0.8); border-color: transparent; }

.error-msg { text-align: center; font-weight: bold; }
.follow-btn:disabled, .unfollow-btn:disabled { opacity: 0.6; cursor: wait; }

.clickable-stat {
  cursor: default;
}
</style>
