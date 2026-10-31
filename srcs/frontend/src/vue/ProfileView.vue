<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const API = '/api';

// --- USER ID TRACKING ---
const currentUserId = ref(null);

// --- MODAL STATES ---
const showFollowModal = ref(false);
const followModalType = ref('');
const followList = ref([]);
const showLogoutModal = ref(false);
const isFollowListLoading = ref(false);

const openFollowModal = async (type) => {
  console.log('profile id:', userProfile.value.id);
  followModalType.value = type;
  showFollowModal.value = true;
  followList.value = [];

  if (!userProfile.value.id) return; // Khass l'id ikoun wajd

  isFollowListLoading.value = true;
  const token = getToken();

  // N3zlo l'endpoint 3la 7sab l'click (followers wla following)
  // T2kked mn sahbek mn l'path s7i7 dyal l'URL
  const endpoint = type === 'following'
    ? `${API}/users/${userProfile.value.id}/following/`
    : `${API}/users/${userProfile.value.id}/followers/`;

  try {
    const response = await fetch(endpoint, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('URL:', response.url, 'status:', response.status, 'type:', response.headers.get('content-type'));
    if (response.ok) {
      const data = await response.json();
      // Kan-adaptiw data li rj3at m3a chno kaytsenna l'HTML dyalna
      // Matalan ila l'backend kayrje3 {id, username, avatar_url}, ghadi nsiftouhom f followList
      followList.value = data.map(user => ({
        id: user.id,
        username: user.username,
        avatar: user.avatar_url ? (user.avatar_url.startsWith('http') ? user.avatar_url : `http://localhost:9000/media/${user.avatar_url}`) : 'https://i.pravatar.cc/150?u=6'
      }));
    } else {
      console.error("Failed to fetch follow list");
    }
  } catch (error) {
    console.error("Error fetching follow list:", error);
  } finally {
    isFollowListLoading.value = false;
  }
};

const closeFollowModal = () => {
  showFollowModal.value = false;
};

// --- AUTH HELPER ---
const getToken = () =>
  localStorage.getItem('token') ||
  localStorage.getItem('access') ||
  localStorage.getItem('access_token');

const openLogoutModal = () => {
  showLogoutModal.value = true;
};

const closeLogoutModal = () => {
  showLogoutModal.value = false;
};

const confirmLogout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('access');
  localStorage.removeItem('access_token');
  router.push('/login');
};

// --- SIDEBAR DATA ---

// --- PROFILE DATA ---
const userProfile = ref({
  id: null,
  name: 'Loading...',
  following: 0,
  followers: 0,
  description: 'Loading...',
  avatar: 'https://i.pravatar.cc/150?u=6',
  isBusiness: false
});

const myEvents = ref([]);
const activeTab = ref('likes');
const activePreviewEvent = ref(null);

// --- FETCH EVENTS (For Business Users) ---
const fetchMyEvents = async () => {
  try {
    const response = await fetch(`${API}/owner/events/`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if (response.ok) {
      myEvents.value = await response.json();
    }
  } catch (error) {
    console.error('Impossibile caricare gli eventi', error);
  }
};

// --- EVENT ACTIONS ---
const goToCreateEvent = () => {
  localStorage.removeItem('editingEvent');
  router.push('/CreateEvent');
};

const openPreview = (event) => {
  activePreviewEvent.value = event;
};

const closePreview = () => {
  activePreviewEvent.value = null;
};

const openEdit = (event) => {
  localStorage.setItem('editingEvent', JSON.stringify(event));
  router.push({ path: '/CreateEvent', query: { edit: 'true' } });
};

const likedVideos = ref([
  { id: 1, title: 'Video 1', thumbnail: '' },
  { id: 2, title: 'Video 2', thumbnail: '' },
]);

// --- INITIAL LOAD ---
onMounted(async () => {
  const token = getToken();
  if (!token) {
    router.push('/login');
    return;
  }

  try {
    const response = await fetch(`${API}/profile/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('access');
      localStorage.removeItem('access_token');
      router.push('/login');
      return;
    }

    if (!response.ok) {
      console.error('Impossibile caricare il profilo, status', response.status);
      return;
    }

    const data = await response.json();
    userProfile.value.id = data.id;
    userProfile.value.name = data.username || '';
    userProfile.value.description = data.bio || '';
    if (data.avatar_url) {
      userProfile.value.avatar = data.avatar_url;
    }
    userProfile.value.following = data.following_count || 0;
    userProfile.value.followers = data.followers_count || 0;
    userProfile.value.isBusiness = (data.type_of_user === 'business');

    if (userProfile.value.isBusiness) {
      activeTab.value = 'events';
      fetchMyEvents();
    }
  } catch (error) {
    console.error('Errore di fetch del profilo', error);
  }
});

// --- EDIT PROFILE MODAL LOGIC ---
const showEditModal = ref(false);
const fileInput = ref(null);
const tempAvatar = ref('');
const selectedFile = ref(null);

const profileEditForm = ref({
  username: '',
  bio: ''
});

const openEditModal = () => {
  profileEditForm.value.username = userProfile.value.name;
  profileEditForm.value.bio = userProfile.value.description;
  tempAvatar.value = userProfile.value.avatar;
  selectedFile.value = null;
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
};

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    tempAvatar.value = URL.createObjectURL(file);
  }
};

const saveProfile = async () => {
  const formData = new FormData();
  formData.append('username', profileEditForm.value.username);
  formData.append('bio', profileEditForm.value.bio);

  if (selectedFile.value) {
    formData.append('avatar_url', selectedFile.value);
  }

  try {
    const response = await fetch(`${API}/profile/update/`, {
      method: 'PATCH',
      headers: { 'Authorization': `Bearer ${getToken()}` },
      body: formData
    });

    const data = await response.json();

    if (response.ok) {
      userProfile.value.name = data.username ?? profileEditForm.value.username;
      userProfile.value.description = data.bio ?? profileEditForm.value.bio;

      if (data.avatar_url) {
        userProfile.value.avatar = data.avatar_url;
      }
      showEditModal.value = false;
    } else {
      console.error('Il backend ha rifiutato il salvataggio:', data);
      const firstError = Object.values(data)[0];
      alert(Array.isArray(firstError) ? firstError[0] : 'Errore durante il salvataggio del profilo.');
    }
  } catch (error) {
    console.error('Errore di rete durante il salvataggio del profilo:', error);
    alert('Impossibile connettersi al server.');
  }
};
</script>

<template>
  <video autoplay muted loop playsinline id="bgVideo">
      <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
  </video>

  <div class="app-container">
    <!-- Navbar -->
    <header class="navbar glass-panel">
      <div class="logo" @click="$router.push('/home')">
        <img src="../assets/logo_temp.png" alt="Ready2Roll Logo" class="nav-logo-img">
        <span class="logo-text">Ready2Roll</span>
      </div>
      <div class="search-bar">
        <input type="text" placeholder="Search...">
      </div>
      <div class="nav-icons">
        <router-link to="/direct" class="nav-icon-link" title="Direct Messages">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" /></svg>
        </router-link>
        <router-link to="/chat" class="nav-icon-link" title="Chat">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 011.037-.443 48.282 48.282 0 005.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" /></svg>
        </router-link>
        <router-link to="/profile" class="nav-icon-link" title="Profile">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>
        </router-link>
      </div>
    </header>

    <div class="main-content">
      <!-- Left Sidebar -->
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

      <!-- Center: Profile Area -->
      <main class="profile-container">
        <!-- Header Profile Info -->
        <div class="profile-header glass-panel">
          <img :src="userProfile.avatar" alt="Avatar" class="profile-avatar">
          <div class="profile-info">
            <div class="name-row">
              <h2>{{ userProfile.name }} <span v-if="userProfile.isBusiness">💼</span></h2>
            </div>
            <div class="stats-row">
              <span class="clickable-stat" @click="openFollowModal('following')">
                <strong>{{ userProfile.following }}</strong> following
              </span>
              <span class="clickable-stat" @click="openFollowModal('followers')">
                <strong>{{ userProfile.followers }}</strong> followers
              </span>
            </div>
            <div class="description-box">
              <p>{{ userProfile.description }}</p>
            </div>
          </div>

          <div class="action-buttons">
            <button v-if="userProfile.isBusiness" class="create-event-btn" @click="goToCreateEvent">
              Create Event 📅
            </button>
            <button class="edit-btn" @click="openEditModal">Edit profile</button>
            <button class="logout-btn" @click="openLogoutModal">Logout</button>
          </div>
        </div>

        <!-- Profile Tabs -->
        <div class="profile-tabs glass-panel">
          <div v-if="userProfile.isBusiness" class="tab" :class="{ active: activeTab === 'events' }" @click="activeTab = 'events'"><span>📅 My Events</span></div>
          <div class="tab" :class="{ active: activeTab === 'likes' }" @click="activeTab = 'likes'"><span>🖤 Likes</span></div>
        </div>

        <!-- EVENTS TAB CONTENT (Business Only) -->
        <div v-if="userProfile.isBusiness && activeTab === 'events'">
          <div v-if="myEvents.length === 0" class="glass-panel" style="text-align: center; padding: 30px; color: #aaa;">
            You haven't created any events yet.
          </div>

          <section class="events-grid">
            <div
              v-for="event in myEvents"
              :key="event.id"
              class="event-reel-card glass-panel"
              @click="openPreview(event)"
            >
              <div class="reel-media-bg">
                <img
                  v-if="event.media_type === 'image'"
                  :src="event.media_src"
                  alt="Event media"
                  class="reel-thumb"
                />
                <video
                  v-else
                  :src="event.media_src"
                  autoplay
                  muted
                  loop
                  playsinline
                  class="reel-thumb"
                ></video>
              </div>

              <span class="status-badge" :class="event.status ? event.status.toLowerCase() : ''">
                {{ event.status }}
              </span>

              <div class="reel-overlay-content">
                <h3 class="event-title">{{ event.title }}</h3>
                <div class="event-info-row">
                  <span>📍 {{ event.location }}</span>
                  <span>📅 {{ event.event_date ? event.event_date.slice(0, 10) : '' }}</span>
                </div>
                <p class="event-description-truncated">
                  {{ event.description || 'No description was inserted' }}
                </p>

                <div class="mini-stats-row">
                  <span>❤️ {{ event.likes_count || 0 }}</span>
                  <span>💬 {{ event.comments_count || 0 }}</span>
                </div>

                <div class="card-actions">
                  <button class="action-btn edit-btn-card" @click.stop="openEdit(event)">
                    ✏️ Edit
                  </button>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- LIKES TAB CONTENT -->
        <div v-else-if="activeTab === 'likes'" class="video-grid">
          <div class="video-card glass-panel" v-for="video in likedVideos" :key="video.id">
            <p class="placeholder-text">video</p>
            <span class="heart-icon">🖤</span>
          </div>
        </div>

      </main>
    </div>
  </div>

  <!-- EVENT STATS & VIDEO MODAL -->
  <div v-if="activePreviewEvent" class="modal-overlay stats-overlay" @click.self="closePreview">
    <div class="stats-modal-card glass-panel">
      <button class="close-modal-btn stats-close-btn" @click="closePreview">✕</button>

      <div class="stats-media-box">
        <img
          v-if="activePreviewEvent.media_type === 'image'"
          :src="activePreviewEvent.media_src"
          alt="Event Media"
          class="stats-media"
        />
        <video
          v-else
          :src="activePreviewEvent.media_src"
          controls
          autoplay
          loop
          playsinline
          class="stats-media"
        ></video>
      </div>

      <div class="stats-info-box">
        <div class="stats-header">
          <span class="status-badge-inline" :class="activePreviewEvent.status ? activePreviewEvent.status.toLowerCase() : ''">
            {{ activePreviewEvent.status }}
          </span>
          <h2>{{ activePreviewEvent.title }}</h2>
          <p class="stats-desc">{{ activePreviewEvent.description || 'No description provided.' }}</p>
        </div>

        <div class="stats-metrics-grid">
          <div class="metric-card">
            <span class="metric-icon">❤️</span>
            <div class="metric-data">
              <strong>{{ activePreviewEvent.likes_count || 0 }}</strong>
              <small>Total Likes</small>
            </div>
          </div>

          <div class="metric-card">
            <span class="metric-icon">💬</span>
            <div class="metric-data">
              <strong>{{ activePreviewEvent.comments_count || 0 }}</strong>
              <small>Comments</small>
            </div>
          </div>

          <div class="metric-card">
            <span class="metric-icon">🎟️</span>
            <div class="metric-data">
              <strong>{{ activePreviewEvent.ticket_price ? `€${activePreviewEvent.ticket_price}` : 'Free' }}</strong>
              <small>Ticket Price</small>
            </div>
          </div>

          <div class="metric-card">
            <span class="metric-icon">👥</span>
            <div class="metric-data">
              <strong>{{ activePreviewEvent.max_capacity || '∞' }}</strong>
              <small>Max Capacity</small>
            </div>
          </div>
        </div>

        <div class="stats-meta-list">
          <div><strong>📍 Location:</strong> {{ activePreviewEvent.location || 'TBD' }}</div>
          <div><strong>📅 Date:</strong> {{ activePreviewEvent.event_date ? activePreviewEvent.event_date.replace('T', ' ').slice(0, 16) : 'TBD' }}</div>
        </div>

        <button class="create-event-btn" style="width: 100%; margin-top: auto;" @click="openEdit(activePreviewEvent)">
          ✏️ Edit this Event
        </button>
      </div>
    </div>
  </div>

<!-- EDIT PROFILE MODAL (Re-styled) -->
  <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
    <div class="modal-content profile-edit-modal glass-panel">
      <div class="modal-header">
        <h3 style="font-family: 'Bruno Ace', sans-serif;">EDIT PROFILE</h3>
        <button class="close-modal-btn stats-close-btn" @click="closeEditModal">✕</button>
      </div>

      <div class="modal-body profile-edit-body">

        <div class="edit-photo-section">
          <div class="photo-edit-area" @click="triggerFileInput">
            <img :src="tempAvatar" alt="avatar" class="edit-avatar-large">
            <div class="edit-overlay-icon">
              <span>✏️</span>
            </div>
            <input
              type="file"
              accept="image/*"
              ref="fileInput"
              class="hidden-file-input"
              @change="handleImageUpload"
            >
          </div>
          <p style="color: #00f2fe; font-size: 0.85rem; margin-top: 10px;">Change Profile Photo</p>
        </div>

        <div class="edit-form-grid">
          <div class="input-group">
            <label>Username</label>
            <input type="text" v-model="profileEditForm.username" placeholder="Username" class="custom-input">
            <p class="helper-text">Usernames can only contain letters, numbers, underscores, and periods.</p>
          </div>

          <div class="input-group">
            <label>Bio</label>
            <textarea v-model="profileEditForm.bio" placeholder="Write a short bio..." rows="4" class="custom-input textarea-input"></textarea>
          </div>
        </div>

      </div>

      <div class="modal-footer profile-edit-footer">
        <button class="cancel-btn" @click="closeEditModal">Cancel</button>
        <button class="save-btn action-btn-cyan" @click="saveProfile">Save Changes</button>
      </div>
    </div>
  </div>

  <!-- FOLLOWERS / FOLLOWING MODAL -->
  <div v-if="showFollowModal" class="modal-overlay" @click.self="closeFollowModal">
    <div class="mini-modal-content">
      <div class="modal-header">
        <h3 style="text-transform: capitalize;">{{ followModalType }}</h3>
        <button class="close-modal-btn" @click="closeFollowModal">✕</button>
      </div>
      <div class="modal-body list-body">
        <ul class="follow-list" v-if="!isFollowListLoading">
          <li v-for="user in followList" :key="user.id" class="follow-item">
            <!-- Tqder tzid hna router-link bach mli tclicki 3la chi 7ed f liste idik l profile dyalo -->
            <router-link :to="{ name: 'UserProfile', params: { id: user.id } }" style="display: flex; align-items: center; gap: 15px; text-decoration: none; color: white;">
              <img :src="user.avatar" alt="avatar" class="avatar-small">
              <span>{{ user.username }}</span>
            </router-link>
          </li>
        </ul>
        <p v-if="isFollowListLoading" style="text-align: center; color: #aaa;">Loading...</p>
        <p v-if="!isFollowListLoading && followList.length === 0" style="text-align: center; color: #aaa;">No users found.</p>
      </div>
    </div>
  </div>

  <!-- LOGOUT CONFIRMATION MODAL -->
  <div v-if="showLogoutModal" class="modal-overlay" @click.self="closeLogoutModal">
    <div class="mini-modal-content">
      <div class="modal-header">
        <h3 style="font-family: Huninn;">Confirm Logout</h3>
        <button class="close-modal-btn" @click="closeLogoutModal">✕</button>
      </div>
      <div class="modal-body" style="text-align: center; padding: 25px 20px;">
        <p style="margin: 0; font-size: 1rem; color: rgba(255, 255, 255, 0.9);">Are you sure you want to logout?</p>
      </div>
      <div class="modal-footer" style="justify-content: center; gap: 10px;">
        <button class="cancel-btn" @click="closeLogoutModal">Cancel</button>
        <button class="logout-confirm-btn" @click="confirmLogout">Logout</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
#bgVideo { position: fixed; top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; z-index: -1; object-fit: cover; }
.app-container { display: flex; flex-direction: column; height: 100vh; color: #FFFFFF; font-family: sans-serif; padding: 10px 20px; box-sizing: border-box; }
.glass-panel { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; box-sizing: border-box; }
.navbar { display: flex; justify-content: space-between; align-items: center; height: 60px; margin-bottom: 15px; flex-shrink: 0; border: 1px solid rgba(255, 255, 255, 0.15); }
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
.avatar { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
.show-more { color: #cccccc; cursor: pointer; font-size: 0.9rem; }
.profile-container { flex-grow: 1; display: flex; flex-direction: column; gap: 15px; overflow-y: auto; scrollbar-width: none; }
.profile-container::-webkit-scrollbar { display: none; }
.profile-header { display: flex; align-items: flex-start; gap: 30px; position: relative; }
.profile-avatar { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; }
.profile-info { display: flex; flex-direction: column; gap: 10px; flex-grow: 1; }
.name-row h2 { margin: 0; display: flex; align-items: center; gap: 5px; }
.stats-row { display: flex; gap: 20px; font-size: 1rem; }
.description-box { background: rgba(255, 255, 255, 0.05); padding: 10px 15px; border-radius: 10px; min-height: 50px; width: 60%; border: 1px solid rgba(255, 255, 255, 0.2); }
.action-buttons {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
}
.edit-btn {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  padding: 10px 20px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}
.edit-btn:hover { background: rgba(255, 255, 255, 0.3); }
.logout-btn {
  background: #d63031;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 10px 20px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}
.logout-btn:hover { background: #ff7675; }
.logout-confirm-btn {
  background: #d63031;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  border: none;
}
.logout-confirm-btn:hover { background: #ff7675; }
.create-event-btn {
  background: #00f2fe;
  color: #000;
  border: none;
  border-radius: 10px;
  padding: 10px 20px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}
.create-event-btn:hover { background: #05d4ca; }
.profile-tabs { display: flex; justify-content: center; padding: 10px; border-radius: 10px; gap: 10px; }
.tab { padding: 10px 40px; font-weight: bold; cursor: pointer; border-bottom: 2px solid transparent; color: rgba(255,255,255,0.6); }
.tab.active { border-bottom-color: #00f2fe; color: white; }
.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
.video-card { aspect-ratio: 9 / 16; display: flex; justify-content: center; align-items: center; position: relative; cursor: pointer; transition: transform 0.2s; }
.video-card:hover { transform: scale(1.02); }
.placeholder-text { font-family: "Bruno Ace", sans-serif; font-size: 1.5rem; opacity: 0.5; }
.heart-icon { position: absolute; bottom: 15px; right: 15px; font-size: 1.5rem; }

/* Tall 9:16 Reel Cards */
.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 18px;
  width: 100%;
}

.event-reel-card {
  aspect-ratio: 9 / 16;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  position: relative;
  overflow: hidden;
  padding: 15px;
  box-sizing: border-box;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.18);
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.event-reel-card:hover {
  transform: translateY(-4px) scale(1.01);
  border-color: rgba(0, 242, 254, 0.6);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.45);
}

.reel-media-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.reel-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 3;
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: bold;
  backdrop-filter: blur(6px);
  text-transform: uppercase;
  pointer-events: none;
}
.status-badge.active { background: rgba(0, 242, 254, 0.3); border: 1px solid #00f2fe; color: #00f2fe; }
.status-badge.draft { background: rgba(255, 193, 7, 0.3); border: 1px solid #ffc107; color: #ffc107; }
.status-badge.scheduled { background: rgba(156, 39, 176, 0.3); border: 1px solid #e040fb; color: #e040fb; }
.status-badge.cancelled { background: rgba(255, 71, 87, 0.3); border: 1px solid #ff4757; color: #ff4757; }

.reel-overlay-content {
  position: relative;
  z-index: 2;
  background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.45) 60%, transparent 100%);
  margin: -15px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  justify-content: flex-end;
  height: 100%;
}

.reel-overlay-content .card-actions {
  pointer-events: auto;
}

.event-title { font-size: 1.1rem; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #FFFFFF; }
.event-info-row { display: flex; flex-direction: column; gap: 2px; font-size: 0.75rem; color: rgba(255, 255, 255, 0.85); }
.event-description-truncated { font-size: 0.75rem; color: rgba(255, 255, 255, 0.7); line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin: 0; }

.mini-stats-row {
  display: flex;
  gap: 14px;
  font-size: 0.8rem;
  font-weight: bold;
  color: #00f2fe;
  margin-top: 2px;
}

.card-actions { display: flex; gap: 8px; margin-top: 5px; }
.action-btn { flex: 1; padding: 6px 10px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.2); background: rgba(255, 255, 255, 0.1); color: #ffffff; font-size: 0.7rem; cursor: pointer; transition: all 0.3s ease; }
.edit-btn-card:hover { background: rgba(255, 255, 255, 0.25); border-color: rgba(255, 255, 255, 0.4); }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: #1e1e1e; width: 500px; max-width: 90%; border-radius: 12px; border: 1px solid #333; color: white; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 1px solid #333; }
.modal-header h3 { margin: 0; font-family: "Bruno Ace", sans-serif; }
.close-modal-btn { background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer; }
.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 20px; max-height: 60vh; overflow-y: auto; }
.modal-section { display: flex; align-items: flex-start; gap: 20px; border-bottom: 1px solid #333; padding-bottom: 20px; }
.modal-section:last-child { border-bottom: none; padding-bottom: 0; }
.modal-section label { width: 120px; font-weight: bold; flex-shrink: 0; }
.input-area { flex-grow: 1; display: flex; flex-direction: column; gap: 5px; }
.input-area input, .input-area textarea, .custom-select { width: 100%; background: #2a2a2a; border: 1px solid #444; color: white; padding: 10px; border-radius: 6px; font-family: inherit; }
.helper-text { font-size: 0.75rem; color: #aaa; margin: 0; }
.photo-edit-area { position: relative; display: inline-block; cursor: pointer; }
.edit-avatar { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; }
.edit-pencil { position: absolute; bottom: 0; right: 0; background: #333; padding: 4px; border-radius: 50%; font-size: 0.8rem; }
.hidden-file-input { display: none; }
.modal-footer { padding: 15px 20px; border-top: 1px solid #333; display: flex; justify-content: flex-end; gap: 10px; }
.modal-footer button { padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; border: none; }
.cancel-btn { background: #333; color: white; }
.cancel-btn:hover { background: #444; }
.save-btn { background: white; color: black; }
.save-btn:hover { background: #ccc; }
.clickable-stat { cursor: pointer; transition: color 0.2s; }
.clickable-stat:hover { color: #00f2fe; }

.mini-modal-content { background: #1e1e1e; width: 350px; max-width: 90%; border-radius: 12px; border: 1px solid #333; color: white; display: flex; flex-direction: column; max-height: 400px; }
.list-body { overflow-y: auto; padding: 10px; }
.follow-list { list-style: none; padding: 0; margin: 0; }
.follow-item { display: flex; align-items: center; gap: 15px; padding: 10px; border-radius: 8px; transition: background 0.2s; }
.follow-item:hover { background: rgba(255, 255, 255, 0.05); }
.avatar-small { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
.user-link { display: flex; align-items: center; gap: 10px; text-decoration: none; color: white; width: 100%; transition: color 0.3s ease; }
.user-link:hover { color: #00f2fe; }

/* Stats Modal */
.stats-overlay {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
}

.stats-modal-card {
  position: relative;
  display: flex;
  gap: 24px;
  background: rgba(20, 20, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 20px;
  max-width: 820px;
  width: 92%;
  max-height: 88vh;
  color: white;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
}

.stats-close-btn {
  position: absolute;
  top: 15px;
  right: 18px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.1);
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stats-media-box {
  height: min(78vh, 560px);
  aspect-ratio: 9 / 16;
  background: #000;
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
}

.stats-media {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.stats-info-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow-y: auto;
  padding-right: 5px;
}

.stats-header h2 {
  margin: 8px 0;
  font-family: "Bruno Ace", sans-serif;
  font-size: 1.4rem;
}

.stats-desc {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.75);
  line-height: 1.4;
}

.status-badge-inline {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: bold;
  text-transform: uppercase;
  border: 1px solid #00f2fe;
  color: #00f2fe;
  background: rgba(0, 242, 254, 0.15);
}

.stats-metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.metric-icon {
  font-size: 1.6rem;
}

.metric-data {
  display: flex;
  flex-direction: column;
}

.metric-data strong {
  font-size: 1.2rem;
  color: #00f2fe;
}

.metric-data small {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.65);
}

.stats-meta-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.88rem;
  background: rgba(255, 255, 255, 0.04);
  padding: 12px 15px;
  border-radius: 10px;
}

/* --- NEW EDIT PROFILE MODAL STYLES --- */
.profile-edit-modal {
  background: rgba(20, 20, 30, 0.95) !important;
  border: 1px solid rgba(0, 242, 254, 0.3) !important;
  max-width: 600px !important;
  border-radius: 20px !important;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
  padding: 0;
}

.profile-edit-modal .modal-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px 30px;
}

.profile-edit-body {
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.edit-photo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.edit-avatar-large {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #00f2fe;
}

.photo-edit-area {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
  transition: transform 0.2s ease;
}

.photo-edit-area:hover {
  transform: scale(1.05);
}

.edit-overlay-icon {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid #00f2fe;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.edit-form-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
}

.input-group label {
  font-weight: bold;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
}

.custom-input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 15px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.4);
  color: #FFFFFF;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
}

.custom-input:focus {
  outline: none;
  border-color: #00f2fe;
}

.textarea-input {
  resize: vertical;
  min-height: 100px;
}

.profile-edit-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px 30px;
}

.action-btn-cyan {
  background: #00f2fe !important;
  color: #000 !important;
  border-radius: 10px;
  padding: 10px 25px;
  font-weight: bold;
  border: none;
  transition: all 0.3s ease;
}

.action-btn-cyan:hover {
  background: #05d4ca !important;
  box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
}

.main-menu ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 5px; }
.menu-item { display: flex; align-items: center; padding: 12px 15px; color: #FFFFFF; text-decoration: none; border-radius: 10px; transition: all 0.2s ease-in-out; cursor: pointer; }
.menu-item:hover { background: rgba(255, 255, 255, 0.1); }

</style>
