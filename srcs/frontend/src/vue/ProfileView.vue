<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const API = 'http://localhost:8000/api';

//to read the name token
const getToken = () =>
  localStorage.getItem('token') ||
  localStorage.getItem('access') ||
  localStorage.getItem('access_token');

// Mock data for the left sidebar
const subscribedAccounts = ref([
  { id: 1, name: 'Xhul', img: 'https://i.pravatar.cc/150?u=1' },
  { id: 2, name: 'Anna', img: 'https://i.pravatar.cc/150?u=2' },
  { id: 3, name: 'thilina', img: 'https://i.pravatar.cc/150?u=3' },
]);


// The active user's profile data
const userProfile = ref({
  name: 'Loading...',
  following: 0,
  followers: 0,
  description: 'Loading...',
  avatar: 'https://i.pravatar.cc/150?u=6' // Default fallback
});

const likedVideos = ref([
  { id: 1, title: 'Video 1', thumbnail: '' },
  { id: 2, title: 'Video 2', thumbnail: '' },
]);

// --- FETCH DATA ON LOAD ---
onMounted(async () => {
  const token = getToken();
  if (!token) {
    router.push('/login'); // not logged in
    return;
  }
  try {
    const response = await fetch(`${API}/profile/`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.status === 401) {
      // token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('access');
      localStorage.removeItem('access_token');
      router.push('/login');
      return;
    }
    if (!response.ok) {
      console.error('could not load profile, status', response.status)
      return ;
    }
    const data = await response.json();
    userProfile.value.name = data.username || '';
    userProfile.value.description = data.bio || '';
    if (data.avatar_url) userProfile.value.avatar = data.avatar_url;
    userProfile.value.following = userProfile.value.following_count || 0;
    userProfile.value.followers = userProfile.value.followers_count || 0;
  } catch (error) {
    console.error('Fetch failed (CORS or server off?)', error);
  }
});

// --- EDIT PROFILE MODAL LOGIC ---
const showEditModal = ref(false);
const fileInput = ref(null);
const tempAvatar = ref('');
const selectedFile = ref(null); // Holds the actual image file to send to Django

const editForm = ref({
  username: '',
  bio: ''
});

const openEditModal = () => {
  editForm.value.username = userProfile.value.name;
  editForm.value.bio = userProfile.value.description;
  tempAvatar.value = userProfile.value.avatar;
  selectedFile.value = null; // Reset file selection
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
    selectedFile.value = file; // Save the file object for the backend
    tempAvatar.value = URL.createObjectURL(file); // Show instant preview
  }
};

const saveProfile = async () => {
  try {
    const response = await fetch(`${API}/profile/update/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({
        username: editForm.value.username,
        bio: editForm.value.bio
      })
    });

    const data = await response.json();

    if (response.ok) {
      userProfile.value.name = data.username ?? editForm.value.username;
      userProfile.value.description = data.bio ?? editForm.value.bio;
      // NOTE: avatar upload needs an ImageField on the backend; not saved yet.
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
            <li @click="$router.push('/home')">🏠 For you</li>
            <li>👤 subscription</li>
            <li>🧭 discover</li>
          </ul>
        </nav>
        <div class="subscribed-list">
          <h3>subscribed accounts</h3>
          <ul>
            <li v-for="account in subscribedAccounts" :key="account.id">
              <img :src="account.img" alt="avatar" class="avatar">
              <span>{{ account.name }}</span>
            </li>
          </ul>
          <p class="show-more">show more ⌄</p>
        </div>
      </aside>

      <!-- Center: Profile Area -->
      <main class="profile-container">

        <div class="profile-header glass-panel">
          <img :src="userProfile.avatar" alt="Profile Avatar" class="profile-avatar">
          <div class="profile-info">
            <div class="name-row">
              <h2>{{ userProfile.name }} 🔒</h2>
            </div>
            <div class="stats-row">
              <span><strong>{{ userProfile.following }}</strong> following</span>
              <span><strong>{{ userProfile.followers }}</strong> followers</span>
            </div>
            <div class="description-box">
              <p>{{ userProfile.description }}</p>
            </div>
          </div>
          <!-- Click qui apre il modal -->
          <button class="edit-btn" @click="openEditModal">edit profile</button>
        </div>

        <div class="profile-tabs glass-panel">
          <div class="tab active"><span>🖤 Likes</span></div>
        </div>

        <div class="video-grid">
          <div class="video-card glass-panel" v-for="video in likedVideos" :key="video.id">
            <p class="placeholder-text">video</p>
            <span class="heart-icon">🖤</span>
          </div>
        </div>

      </main>
    </div>
  </div>

  <!-- EDIT PROFILE MODAL -->
  <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
    <div class="modal-content">
      <!-- Header -->
      <div class="modal-header">
        <h3>Edit profile</h3>
        <button class="close-modal-btn" @click="closeEditModal">✕</button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">

        <!-- Profile Photo (Clickable for upload) -->
        <div class="modal-section row-section">
          <label>Profile photo</label>
          <div class="photo-edit-area" @click="triggerFileInput">
            <img :src="tempAvatar" alt="avatar" class="edit-avatar">
            <span class="edit-pencil">✏️</span>
            <!-- Hidden file input -->
            <input
              type="file"
              accept="image/*"
              ref="fileInput"
              class="hidden-file-input"
              @change="handleImageUpload"
            >
          </div>
        </div>

        <!-- Username -->
        <div class="modal-section row-section">
          <label>Username</label>
          <div class="input-area">
            <input type="text" v-model="editForm.username" placeholder="Username">
            <p class="helper-text">Usernames can only contain letters, numbers, underscores, and periods. Changing your username will also change your profile link.</p>
          </div>
        </div>

        <!-- Bio -->
        <div class="modal-section row-section">
          <label>Bio</label>
          <div class="input-area">
            <textarea v-model="editForm.bio" placeholder="Bio" rows="4"></textarea>
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button class="cancel-btn" @click="closeEditModal">cancel</button>
        <button class="save-btn" @click="saveProfile">save</button>
      </div>
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
.edit-btn { background: #d63031; color: white; border: none; border-radius: 10px; padding: 10px 20px; font-weight: bold; cursor: pointer; position: absolute; bottom: 20px; right: 20px; transition: background 0.3s; }
.edit-btn:hover { background: #ff7675; }

.profile-tabs { display: flex; justify-content: center; padding: 10px; border-radius: 10px; }
.tab { padding: 10px 40px; font-weight: bold; cursor: pointer; border-bottom: 2px solid #00f2fe; color: white; }

.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
.video-card { aspect-ratio: 9 / 16; display: flex; justify-content: center; align-items: center; position: relative; cursor: pointer; transition: transform 0.2s; }
.video-card:hover { transform: scale(1.02); }
.placeholder-text { font-family: "Bruno Ace", sans-serif; font-size: 1.5rem; opacity: 0.5; }
.heart-icon { position: absolute; bottom: 15px; right: 15px; font-size: 1.5rem; }

/* =========================================
   MODAL STYLES
   ========================================= */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #1e1e1e;
  width: 500px;
  max-width: 90%;
  border-radius: 12px;
  border: 1px solid #333;
  color: white;
  display: flex; flex-direction: column;
}

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px;
  border-bottom: 1px solid #333;
}
.modal-header h3 { margin: 0; font-family: "Bruno Ace", sans-serif; }
.close-modal-btn {
  background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer;
}

.modal-body {
  padding: 20px;
  display: flex; flex-direction: column; gap: 20px;
}

.modal-section {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  border-bottom: 1px solid #333;
  padding-bottom: 20px;
}
.modal-section:last-child { border-bottom: none; padding-bottom: 0; }

.modal-section label {
  width: 120px;
  font-weight: bold;
  flex-shrink: 0;
}

.input-area {
  flex-grow: 1;
  display: flex; flex-direction: column; gap: 5px;
}

.input-area input, .input-area textarea {
  width: 100%;
  background: #2a2a2a;
  border: 1px solid #444;
  color: white;
  padding: 10px;
  border-radius: 6px;
  font-family: inherit;
}
.helper-text {
  font-size: 0.75rem; color: #aaa; margin: 0;
}

.photo-edit-area {
  position: relative;
  display: inline-block;
  cursor: pointer;
}
.edit-avatar {
  width: 80px; height: 80px; border-radius: 50%; object-fit: cover;
}
.edit-pencil {
  position: absolute; bottom: 0; right: 0;
  background: #333; padding: 4px; border-radius: 50%; font-size: 0.8rem;
}
.hidden-file-input {
  display: none;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #333;
  display: flex; justify-content: flex-end; gap: 10px;
}
.modal-footer button {
  padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; border: none;
}
.cancel-btn { background: #333; color: white; }
.cancel-btn:hover { background: #444; }
.save-btn { background: white; color: black; }
.save-btn:hover { background: #ccc; }
</style>
