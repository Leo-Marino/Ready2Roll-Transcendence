<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const API = '/api';

// For following and followers modals
const showFollowModal = ref(false);
const followModalType = ref('');
const followList = ref([]);

const openFollowModal = async (type) => {
  followModalType.value = type;
  showFollowModal.value = true;
  followList.value = [];

  if (type == 'following') {
    followList.value = [
      { id: 1, username: 'Xhul', avatar: 'https://i.pravatar.cc/150?u=1' },
      { id: 2, username: 'Anna', avatar: 'https://i.pravatar.cc/150?u=2' }
    ];
  } else if (type == 'followers') {
    followList.value = [
      { id: 3, username: 'thilina', avatar: 'https://i.pravatar.cc/150?u=3' },
      { id: 4, username: 'Milko', avatar: 'https://i.pravatar.cc/150?u=4' }
    ];
  }
};

const closeFollowModal = () => {
  showFollowModal.value = false;
};

// Token helper
const getToken = () =>
  localStorage.getItem('token') ||
  localStorage.getItem('access') ||
  localStorage.getItem('access_token');


// The active user's profile data
const userProfile = ref({
  name: 'Loading...',
  following: 0,
  followers: 0,
  description: 'Loading...',
  avatar: 'https://i.pravatar.cc/150?u=6',
  isBusiness: false
});

const myEvents = ref([]);
const activeTab = ref('likes');

// Event management states (from OwnerEventView)
const activePreviewEvent = ref(null);
const isEditing = ref(false);
const editForm = ref({
  id: null,
  title: '',
  location: '',
  event_date: '',
  status: 'active',
  description: '',
  media_type: 'image',
  media_src: ''
});
const editFileInput = ref(null);

const fetchMyEvents = async () => {
  try {
    const response = await fetch(`${API}/owner/events/`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if (response.ok) {
      myEvents.value = await response.json();
    }
  } catch (error) {
    console.error('Could not load my events', error);
  }
};

// Event Actions
const goToCreateEvent = () => {
  router.push('/CreateEvent');
};

const openPreview = (event) => {
  activePreviewEvent.value = event;
};

const closePreview = () => {
  activePreviewEvent.value = null;
};

const openEdit = (event) => {
  editForm.value = { ...event };
  isEditing.value = true;
};

const closeEdit = () => {
  isEditing.value = false;
};

const triggerEditFileInput = () => {
  if (editFileInput.value) {
    editFileInput.value.click();
  }
};

const handleEditFileUpload = (e) => {
  const file = e.target.files[0];
  if (file) {
    editForm.value.media_src = URL.createObjectURL(file);
    editForm.value.media_type = file.type.startsWith('video') ? 'video' : 'image';
  }
};

const saveEdit = async () => {
  const token = getToken();
  const payload = {
    title: editForm.value.title,
    location: editForm.value.location,
    event_date: editForm.value.event_date,
    status: editForm.value.status,
    description: editForm.value.description,
    media_type: editForm.value.media_type,
    media_src: editForm.value.media_src
  };

  try {
    const response = await fetch(`${API}/events/${editForm.value.id}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      const updatedEvent = await response.json();
      const index = myEvents.value.findIndex(e => e.id === editForm.value.id);
      if (index !== -1) {
        myEvents.value.splice(index, 1, updatedEvent);
      }
      alert("Event updated successfully!");
      closeEdit();
    } else {
      const errData = await response.json();
      console.error("Error updating event:", errData);
      alert("Error saving changes.");
    }
  } catch (error) {
    console.error("Network error during save:", error);
    alert("Unable to connect to the backend server.");
  }
};

const likedVideos = ref([
  { id: 1, title: 'Video 1', thumbnail: '' },
  { id: 2, title: 'Video 2', thumbnail: '' },
]);

// --- FETCH DATA ON LOAD ---
onMounted(async () => {
  const token = getToken();
  if (!token) {
    router.push('/login');
    return;
  }
  try {
    const response = await fetch(`${API}/profile/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('access');
      localStorage.removeItem('access_token');
      router.push('/login');
      return;
    }
    if (!response.ok) {
      console.error('could not load profile, status', response.status);
      return;
    }
    const data = await response.json();
    userProfile.value.name = data.username || '';
    userProfile.value.description = data.bio || '';
    if (data.avatar_url) {
      userProfile.value.avatar = data.avatar_url;
    }
    userProfile.value.following = data.following_count || 2;
    userProfile.value.followers = data.followers_count || 3;
    userProfile.value.isBusiness = (data.type_of_user === 'business');

    if (userProfile.value.isBusiness) {
      activeTab.value = 'events';
      fetchMyEvents();
    }
  } catch (error) {
    console.error('Fetch failed (CORS or server off?)', error);
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
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
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
      console.error('Backend rejected the save:', data);
      const firstError = Object.values(data)[0];
      alert(Array.isArray(firstError) ? firstError[0] : 'Error saving profile.');
    }
  } catch (error) {
    console.error('Network error saving profile:', error);
    alert('Unable to connect to the server.');
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

        <div class="profile-header glass-panel">
          <img :src="userProfile.avatar" alt="Avatar" class="profile-avatar">
          <div class="profile-info">
            <div class="name-row">
              <h2>{{ userProfile.name }} 🔒</h2>
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
              create Event 📅
            </button>
            <button class="edit-btn" @click="openEditModal">edit profile</button>
          </div>
        </div>

        <!-- Profile Tabs -->
        <div class="profile-tabs glass-panel">
          <div v-if="userProfile.isBusiness" class="tab" :class="{ active: activeTab === 'events' }" @click="activeTab = 'events'"><span>🎬 My events</span></div>
          <div class="tab" :class="{ active: activeTab === 'likes' }" @click="activeTab = 'likes'"><span>🖤 Likes</span></div>
        </div>

        <!-- Events Tab Content (Reels Format matching Likes Section) -->
        <div v-if="userProfile.isBusiness && activeTab === 'events'">
          <div v-if="myEvents.length === 0" class="glass-panel" style="text-align: center; padding: 30px; color: #aaa;">
            You haven't created any events yet.
          </div>
          <section class="events-grid">
            <div
              v-for="event in myEvents"
              :key="event.id"
              class="event-reel-card glass-panel"
            >
              <!-- Background Media Content (Clickable to open preview) -->
              <div class="reel-media-bg" @click="openPreview(event)">
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

              <!-- Status Badge -->
              <span class="status-badge" :class="event.status ? event.status.toLowerCase() : ''">
                {{ event.status }}
              </span>

              <!-- Content Overlay on top of Media -->
              <div class="reel-overlay-content">
                <h3 class="event-title">{{ event.title }}</h3>
                <div class="event-info-row">
                  <span>📍 {{ event.location }}</span>
                  <span>📅 {{ event.event_date }}</span>
                </div>
                <p class="event-description-truncated">
                  {{ event.description || 'No description was inserted' }}
                </p>

                <div class="card-actions">
                  <button class="action-btn edit-btn-card" @click="openEdit(event)">
                    Edit
                  </button>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- Likes Tab Content -->
        <div v-else-if="activeTab === 'likes'" class="video-grid">
          <div class="video-card glass-panel" v-for="video in likedVideos" :key="video.id">
            <p class="placeholder-text">video</p>
            <span class="heart-icon">🖤</span>
          </div>
        </div>

      </main>
    </div>
  </div>

  <!-- EVENT PREVIEW REEL MODAL (Scrollable feed of all posted events) -->
  <div v-if="activePreviewEvent" class="modal-overlay preview-overlay" @click.self="closePreview">
    <div class="preview-reel-container">
      <button class="close-modal-btn preview-close" @click="closePreview">✕</button>
      <div class="preview-scroll-wrapper">
        <div
          v-for="event in myEvents"
          :key="event.id"
          class="preview-reel-card"
        >
          <div class="preview-media-wrapper">
            <video
              v-if="event.media_type === 'video'"
              :src="event.media_src"
              autoplay
              muted
              loop
              playsinline
              class="preview-media-content"
            ></video>
            <img
              v-else
              :src="event.media_src"
              alt="Event Preview"
              class="preview-media-content"
            />
          </div>
          <div class="preview-overlay-content">
            <div class="preview-user-info">
              <img :src="userProfile.avatar" alt="avatar" class="preview-avatar" />
              <span class="preview-username">{{ userProfile.name }}</span>
            </div>
            <h2 class="preview-title">{{ event.title }}</h2>
            <p class="preview-desc">{{ event.description || 'No description provided.' }}</p>
            <div class="preview-meta">
              <span>📍 {{ event.location }}</span>
              <span>📅 {{ event.event_date }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- EDIT PROFILE MODAL -->
  <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Edit profile</h3>
        <button class="close-modal-btn" @click="closeEditModal">✕</button>
      </div>

      <div class="modal-body">
        <div class="modal-section row-section">
          <label>Profile photo</label>
          <div class="photo-edit-area" @click="triggerFileInput">
            <img :src="tempAvatar" alt="avatar" class="edit-avatar">
            <span class="edit-pencil">✏️</span>
            <input
              type="file"
              accept="image/*"
              ref="fileInput"
              class="hidden-file-input"
              @change="handleImageUpload"
            >
          </div>
        </div>

        <div class="modal-section row-section">
          <label>Username</label>
          <div class="input-area">
            <input type="text" v-model="profileEditForm.username" placeholder="Username">
            <p class="helper-text">Usernames can only contain letters, numbers, underscores, and periods.</p>
          </div>
        </div>

        <div class="modal-section row-section">
          <label>Bio</label>
          <div class="input-area">
            <textarea v-model="profileEditForm.bio" placeholder="Bio" rows="4"></textarea>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="cancel-btn" @click="closeEditModal">cancel</button>
        <button class="save-btn" @click="saveProfile">save</button>
      </div>
    </div>
  </div>

  <!-- EDIT EVENT MODAL -->
  <div v-if="isEditing" class="modal-overlay" @click.self="closeEdit">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Edit Event</h3>
        <button class="close-modal-btn" @click="closeEdit">✕</button>
      </div>
      <div class="modal-body">
        <div class="modal-section row-section">
          <label>Title</label>
          <div class="input-area"><input type="text" v-model="editForm.title"></div>
        </div>
        <div class="modal-section row-section">
          <label>Location</label>
          <div class="input-area"><input type="text" v-model="editForm.location"></div>
        </div>
        <div class="modal-section row-section">
          <label>Date</label>
          <div class="input-area"><input type="date" v-model="editForm.event_date"></div>
        </div>
        <div class="modal-section row-section">
          <label>Status</label>
          <div class="input-area">
            <select v-model="editForm.status" class="custom-select">
              <option value="Active">Active</option>
              <option value="Draft">Draft</option>
              <option value="Scheduled">Scheduled</option>
            </select>
          </div>
        </div>
        <div class="modal-section row-section">
          <label>Description</label>
          <div class="input-area"><textarea v-model="editForm.description" rows="3"></textarea></div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="closeEdit">Cancel</button>
        <button class="save-btn" @click="saveEdit">Save Changes</button>
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
        <ul class="follow-list">
          <li v-for="user in followList" :key="user.id" class="follow-item">
            <img :src="user.avatar" alt="avatar" class="avatar-small">
            <span>{{ user.username }}</span>
          </li>
        </ul>
        <p v-if="followList.length === 0" style="text-align: center; color: #aaa;">No users found.</p>
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

.action-buttons {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
}

.edit-btn {
  background: #d63031;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 10px 20px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}
.edit-btn:hover { background: #ff7675; }

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

.video-grid, .events-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
.video-card { aspect-ratio: 9 / 16; display: flex; justify-content: center; align-items: center; position: relative; cursor: pointer; transition: transform 0.2s; }
.video-card:hover { transform: scale(1.02); }
.placeholder-text { font-family: "Bruno Ace", sans-serif; font-size: 1.5rem; opacity: 0.5; }
.heart-icon { position: absolute; bottom: 15px; right: 15px; font-size: 1.5rem; }

.event-reel-card {
  aspect-ratio: 9 / 16;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  position: relative;
  overflow: hidden;
  padding: 15px;
  box-sizing: border-box;
  transition: transform 0.2s;
}
.event-reel-card:hover { transform: scale(1.02); }

.reel-media-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  cursor: pointer;
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

.reel-overlay-content {
  position: relative;
  z-index: 2;
  background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 60%, transparent 100%);
  margin: -15px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  justify-content: flex-end;
  height: 100%;
  pointer-events: none;
}

.reel-overlay-content .card-actions {
  pointer-events: auto;
}

.event-title { font-size: 1.1rem; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #FFFFFF; }
.event-info-row { display: flex; flex-direction: column; gap: 2px; font-size: 0.75rem; color: rgba(255, 255, 255, 0.85); }
.event-description-truncated { font-size: 0.75rem; color: rgba(255, 255, 255, 0.7); line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin: 0; }

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

/* Preview Reel Modal Styles with Vertical Scroll */
.preview-overlay {
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
}

.preview-reel-container {
  position: relative;
  width: 380px;
  height: 680px;
  max-width: 95vw;
  max-height: 90vh;
  background: #111;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  display: flex;
  box-shadow: 0 15px 35px rgba(0,0,0,0.6);
}

.preview-scroll-wrapper {
  width: 100%;
  height: 100%;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
  scrollbar-width: none;
}
.preview-scroll-wrapper::-webkit-scrollbar {
  display: none;
}

.preview-close {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 20;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.preview-reel-card {
  position: relative;
  width: 100%;
  height: 100%;
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.preview-media-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.preview-media-content {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-overlay-content {
  position: relative;
  z-index: 2;
  padding: 20px;
  background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.4) 60%, transparent 100%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
  width: 100%;
  box-sizing: border-box;
}

.preview-user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.preview-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #00f2fe;
}

.preview-username {
  font-weight: bold;
  font-size: 0.95rem;
  color: #FFFFFF;
}

.preview-title {
  margin: 0;
  font-size: 1.2rem;
  font-family: "Bruno Ace", sans-serif;
  color: #FFFFFF;
}

.preview-desc {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.preview-meta {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 0.78rem;
  color: #00f2fe;
  margin-top: 4px;
}
</style>
