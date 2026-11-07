<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import EventMediaGrid from './EventMediaGrid.vue';//xh
import SearchBar from './SearchBar.vue';
import { useSocialSocket } from '../composables/useSocialSocket';
import NotificationBell from './NotificationBell.vue';
import ChatNavLink from './ChatNavLink.vue';

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

// --- MAP MODAL STATE ---
const showMapModal = ref(false);
const activeMapLocation = ref('');
const activeMapTitle = ref('');

const openMapModal = (location, title, event) => {
  if (event) event.stopPropagation();
  activeMapLocation.value = location || 'Florence, Italy';
  activeMapTitle.value = title || 'Event Location';
  showMapModal.value = true;
};

const closeMapModal = () => {
  showMapModal.value = false;
};

const openFollowModal = async (type) => {
  console.log('profile id:', userProfile.value.id);
  followModalType.value = type;
  showFollowModal.value = true;
  followList.value = [];

  if (!userProfile.value.id) return;

  isFollowListLoading.value = true;
  const token = getToken();

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

// --- PROFILE DATA ---
const userProfile = ref({
  id: null,
  name: 'Loading...',
  following: 0,
  followers: 0,
  description: '',
  avatar: 'https://i.pravatar.cc/150?u=6',
  isBusiness: false
});

const myEvents = ref([]);
const likedVideos = ref([
  { id: 1, title: 'Video 1', media_type: 'image', media_src: '' },
  { id: 2, title: 'Video 2', media_type: 'image', media_src: '' },
]);
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

// ----- xh events like start--------
const likedEvents = ref([]);

const fetchLikedEvents = async () => {
  try {
    const response = await fetch(`${API}/social/liked-events/`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if (response.ok) {
      likedEvents.value = await response.json();
    }
  } catch (error) {
    console.error('Impossible to uplod the liked video', error);
  }
};

// ricarica ogni volta che apri il tab (così vedi i like fatti nel frattempo)
watch(activeTab, (tab) => {
  if (tab === 'likes') fetchLikedEvents();
});

//------xh event like end ---------

// --- Live updates from other users (WebSocket) ---
// Followers counter and likes/comments counters of the events shown on this page.
const handleSocialMessage = (message) => {
  const { action, target_id: targetId, data } = message;

  if (action === 'follow') {
    if (targetId === userProfile.value.id) {
      userProfile.value.followers = data.followers_count;
    }
  } else if (action === 'like' || action === 'comment') {
    const lists = [myEvents.value, likedEvents.value];
    if (activePreviewEvent.value) lists.push([activePreviewEvent.value]);
    lists.forEach((list) => {
      list.forEach((ev) => {
        if (ev.id !== targetId) return;
        if (action === 'like') ev.likes_count = data.likes_count;
        else ev.comments_count = data.comments_count;
      });
    });
  } else if (action === 'update_profile') {
    // ---> ADDED THIS BLOCK FOR LIVE PROFILE UPDATES <---
    if (targetId === userProfile.value.id) {
      userProfile.value.name = data.username;
      userProfile.value.description = data.user_bio;
      if (data.user_avatar) {
         userProfile.value.avatar = data.user_avatar;
      }
    }
  } else if (action === 'resync') {
    fetchMyEvents();
    if (activeTab.value === 'likes') fetchLikedEvents();
  }
};

useSocialSocket(handleSocialMessage);

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
    //------xh events like-----
    //------xh evetns like-----
    if (userProfile.value.isBusiness) {
      activeTab.value = 'events';
      fetchMyEvents();
    } else {
      activeTab.value = 'likes';
    }
    fetchLikedEvents();
  } catch (error) {
    console.error('Errore di fetch del profilo', error);
  }

});

// --- EDIT PROFILE MODAL LOGIC ---
const showEditModal = ref(false);
const fileInput = ref(null);
const tempAvatar = ref('');
const selectedFile = ref(null);
const profileEditUsernameError = ref('');
const usernamePattern = /^[A-Za-z0-9_.]+$/;

const profileEditForm = ref({
  username: '',
  bio: ''
});

const openEditModal = () => {
  profileEditForm.value.username = userProfile.value.name;
  profileEditForm.value.bio = userProfile.value.description;
  profileEditUsernameError.value = '';
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
  if (!usernamePattern.test(profileEditForm.value.username)) {
    profileEditUsernameError.value =
      'Usernames can only contain letters, numbers, underscores, and periods.';
    return;
  }
  profileEditUsernameError.value = '';

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
      <!-- <div class="search-bar">
        <input type="text" placeholder="Search...">
      </div> -->
      <SearchBar />
      <div class="nav-icons">
        <ChatNavLink title="Chat">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" /></svg>
        </ChatNavLink>
        <NotificationBell />
        <!-- <router-link to="/chat" class="nav-icon-link" title="Chat">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" /></svg>
        </router-link> -->
        <router-link to="/profile" class="nav-icon-link" title="Profile">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>
        </router-link>
      </div>
    </header>

        <div class="main-content">
      <aside class="left-sidebar glass-panel">
        <nav class="main-menu">
          <h3>Menu</h3>
          <ul>
            <li @click="$router.push('/home')" class="menu-item">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="menu-svg-icon"
              >
                <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/>
                <path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              </svg>
              <span>For you</span>
            </li>
            <li @click="$router.push('/subscriptions')" class="menu-item">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="menu-svg-icon"
              >
                <path d="M16.051 12.616a1 1 0 0 1 1.909.024l.737 1.452a1 1 0 0 0 .737.535l1.634.256a1 1 0 0 1 .588 1.806l-1.172 1.168a1 1 0 0 0-.282.866l.259 1.613a1 1 0 0 1-1.541 1.134l-1.465-.75a1 1 0 0 0-.912 0l-1.465.75a1 1 0 0 1-1.539-1.133l.258-1.613a1 1 0 0 0-.282-.866l-1.156-1.153a1 1 0 0 1 .572-1.822l1.633-.256a1 1 0 0 0 .737-.535z"/>
                <path d="M8 15H7a4 4 0 0 0-4 4v2"/><circle cx="10" cy="7" r="4"/>
              </svg>
              <span>subscriptions</span>
            </li>
            <li @click="$router.push('/discover')" class="menu-item">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="menu-svg-icon">
                  <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                  <path d="M8 16l2 -6l6 -2l-2 6l-6 2" />
                  <path d="M3 12a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
                  <path d="M12 3l0 2" />
                  <path d="M12 19l0 2" />
                  <path d="M3 12l2 0" />
                  <path d="M19 12l2 0" />
                </svg>
              <span>discover</span>
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
                <h2>
                  {{ userProfile.name }}
                  <!-- VERIFIED BADGE (Cyan background with WHITE tick) -->
                 <svg v-if="userProfile.isBusiness" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="#00f2fe" stroke="#00f2fe" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="verified-badge" title="Business Account">
                   <path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"/>
                   <!-- Had l'path hwa l'tick, dertlih stroke byad w ghelledt l'khett chwya bach yban wadeh -->
                   <path d="m16 9-5.5 5.5L8 12" stroke="#ffffff" stroke-width="2.5"/>
                 </svg>
               </h2>
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
              <p :class="{ 'empty-bio': !userProfile.description }">
                {{ userProfile.description || 'This user has not set a bio yet' }}
              </p>
            </div>
          </div>

          <div class="action-buttons-styled">
            <button v-if="userProfile.isBusiness" class="action-pill create-pill" @click="goToCreateEvent">
              <span>Create Event</span>
            </button>
            <button class="action-pill edit-pill" @click="openEditModal">
              <span>Edit Profile</span>
            </button>
            <button class="action-pill logout-pill" @click="openLogoutModal">
              <span>Logout</span>
            </button>
          </div>
        </div>

        <!-- Profile Tabs -->
        <div class="profile-tabs glass-panel">
          <div
            v-if="userProfile.isBusiness"
            class="tab"
            :class="{ active: activeTab === 'events' }"
            @click="activeTab = 'events'"
          >
            <span class="tab-label">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="tab-icon"
              >
                <path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M8 13h.01"/><path d="M12 13h.01"/><path d="M16 13h.01"/><path d="M8 17h.01"/><path d="M12 17h.01"/><path d="M16 17h.01"/>
              </svg>
              My Events
            </span>
          </div>

          <div
            class="tab"
            :class="{ active: activeTab === 'likes' }"
            @click="activeTab = 'likes'"
          >
            <span class="tab-label">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="tab-icon"
              >
                <path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"/>
              </svg>
              Likes
            </span>
          </div>
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

<!-- Content Overlay on top of Media -->
              <div class="reel-overlay-content">
                <h3 class="event-title">{{ event.title }}</h3>

                <div class="event-info-row">
                  <span class="meta-item clickable-location" @click="openMapModal(event.location, event.title, $event)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ui-icon lucide lucide-map-pin"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>
                    {{ event.location || 'Location TBD' }}
                  </span>

                  <span class="meta-item">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ui-icon lucide lucide-calendar-days"><path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M8 13h.01"/><path d="M12 13h.01"/><path d="M16 13h.01"/><path d="M8 17h.01"/><path d="M12 17h.01"/><path d="M16 17h.01"/></svg>
                    {{ event.event_date ? event.event_date.slice(0, 10) : '' }}
                  </span>
                </div>

                <p class="event-description-truncated">
                  {{ event.description || 'No description was inserted' }}
                </p>

                <!-- Quick mini stats on card -->
                <div class="mini-stats-row">
                  <span class="meta-item">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ui-icon lucide lucide-heart"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"/></svg>
                    {{ event.likes_count || 0 }}
                  </span>
                  <span class="meta-item">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ui-icon lucide lucide-message-circle-more"><path d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719"/><path d="M8 12h.01"/><path d="M12 12h.01"/><path d="M16 12h.01"/></svg>
                    {{ event.comments_count || 0 }}
                  </span>
                </div>

                <!-- Edit Button -->
                <div class="card-actions">
                    <button class="action-btn edit-btn-card" style="display: flex; align-items: center; justify-content: center; gap: 6px;" @click.stop="openEdit(event)">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-pen"><path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/></svg>
                      Edit
                    </button>
                  </div>
                </div>
              </div>
            </section>
          </div>

        <!-- LIKES TAB CONTENT xh -->
        <div v-else-if="activeTab === 'likes'">
          <EventMediaGrid
            :events="likedEvents"
            empty-text="You haven't liked any videos yet."
          />
        </div>
        <!-- LIKES TAB CONTENT xh -->
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
          <span class="status-badge-inline" :class="activePreviewEvent.status ? activePreviewEvent.status.toLowerCase() : ''" v-if="activePreviewEvent.status">
            {{ activePreviewEvent.status }}
          </span>
          <h2>{{ activePreviewEvent.title }}</h2>
          <p class="stats-desc">{{ activePreviewEvent.description || 'No description provided.' }}</p>
        </div>

<!-- Big Stats Counters -->
        <div class="stats-metrics-grid">

          <!-- LIKES (Static Display) -->
          <div class="metric-card">
            <span class="metric-icon-wrap">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-heart"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"/></svg>
            </span>
            <div class="metric-data">
              <strong>{{ activePreviewEvent.likes_count || 0 }}</strong>
              <small>Total Likes</small>
            </div>
          </div>

          <!-- COMMENTS -->
          <div class="metric-card">
            <span class="metric-icon-wrap">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-message-circle-more"><path d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719"/><path d="M8 12h.01"/><path d="M12 12h.01"/><path d="M16 12h.01"/></svg>
            </span>
            <div class="metric-data">
              <strong>{{ activePreviewEvent.comments_count || 0 }}</strong>
              <small>Comments</small>
            </div>
          </div>

          <!-- TICKET PRICE -->
          <div class="metric-card">
            <span class="metric-icon-wrap">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-ticket"><path stroke="none" d="M0 0h24v24H0z" fill="none" /><path d="M15 5l0 2" /><path d="M15 11l0 2" /><path d="M15 17l0 2" /><path d="M5 5h14a2 2 0 0 1 2 2v3a2 2 0 0 0 0 4v3a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-3a2 2 0 0 0 0 -4v-3a2 2 0 0 1 2 -2" /></svg>
            </span>
            <div class="metric-data">
              <strong>{{ activePreviewEvent.ticket_price ? `€${activePreviewEvent.ticket_price}` : 'Free' }}</strong>
              <small>Ticket Price</small>
            </div>
          </div>

          <!-- CAPACITY -->
          <div class="metric-card">
            <span class="metric-icon-wrap">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-users"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><path d="M16 3.128a4 4 0 0 1 0 7.744"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><circle cx="9" cy="7" r="4"/></svg>
            </span>
            <div class="metric-data">
              <strong>{{ activePreviewEvent.max_capacity || '∞' }}</strong>
              <small>Max Capacity</small>
            </div>
          </div>
        </div>

        <!-- Extra Info (Location & Date) -->
        <div class="stats-meta-list">
          <div class="meta-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ui-icon lucide lucide-map-pin"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/></svg>
            <span><strong>Location:</strong> {{ activePreviewEvent.location || 'TBD' }}</span>
          </div>
          <div class="meta-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ui-icon lucide lucide-calendar-days"><path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M8 13h.01"/><path d="M12 13h.01"/><path d="M16 13h.01"/><path d="M8 17h.01"/><path d="M12 17h.01"/><path d="M16 17h.01"/></svg>
            <span><strong>Date:</strong> {{ activePreviewEvent.event_date ? activePreviewEvent.event_date.replace('T', ' ').slice(0, 16) : 'TBD' }}</span>
          </div>
        </div>

        <!-- <div class="stats-meta-list" v-if="activePreviewEvent.location">
          <div>
            <strong>📍 Location:</strong>
            <span class="clickable-location" @click="openMapModal(activePreviewEvent.location, activePreviewEvent.title)">
              {{ activePreviewEvent.location }} 🗺️ (View Map)
            </span>
          </div>
          <div><strong>📅 Date:</strong> {{ activePreviewEvent.event_date ? activePreviewEvent.event_date.replace('T', ' ').slice(0, 16) : 'TBD' }}</div>
        </div> -->

          <div style="display: flex; gap: 10px; margin-top: auto;">
          <!-- EDIT BUTTON -->
            <button v-if="userProfile.isBusiness && activePreviewEvent.id" class="action-btn edit-btn-card" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;" @click="openEdit(activePreviewEvent)">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-pen"><path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/></svg>
              Edit
            </button>

          <!-- DELETE BUTTON -->
            <button v-if="userProfile.isBusiness && activePreviewEvent.id" class="action-btn delete-btn-card" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 12px; font-size: 0.85rem;" @click="deleteEvent(activePreviewEvent)">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trash"><path d="M10 11v6"/><path d="M14 11v6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

  <!-- MAP POPUP MODAL (Larger Size) -->
  <div v-if="showMapModal" class="modal-overlay" @click.self="closeMapModal">
    <div class="modal-content map-modal-card glass-panel">
      <div class="modal-header">
        <h3>📍 {{ activeMapTitle }}</h3>
        <button class="close-modal-btn stats-close-btn" @click="closeMapModal">✕</button>
      </div>
      <div class="map-modal-body">
        <p style="margin-top: 0; color: #00f2fe; font-size: 0.95rem;">{{ activeMapLocation }}</p>
        <div class="map-popup-wrapper">
          <iframe
            width="100%"
            height="100%"
            frameborder="0"
            scrolling="no"
            marginheight="0"
            marginwidth="0"
            :src="`https://maps.google.com/maps?q=${encodeURIComponent(activeMapLocation)}&t=&z=16&ie=UTF8&iwloc=&output=embed`"
            class="map-iframe-popup"
          ></iframe>
        </div>
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
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-pen"><path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z"/></svg>
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
            <p
              class="helper-text"
              :class="{ 'username-error-text': profileEditUsernameError }"
            >
              Usernames can only contain letters, numbers, underscores, and periods.
            </p>
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
.name-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.name-row h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px; /* Tiser 3la smya */

}

.verified-badge {
  display: inline-block;
  margin-bottom: 2px; /* Kat9adha m3a l'ktaba */
}

.stats-row { display: flex; gap: 20px; font-size: 1rem; }
.description-box { background: rgba(255, 255, 255, 0.05); padding: 10px 15px; border-radius: 10px; min-height: 50px; width: 60%; border: 1px solid rgba(255, 255, 255, 0.2); }
.empty-bio { color: rgba(255, 255, 255, 0.4); font-style: italic; }
.action-buttons-styled {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.action-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 12px;
  font-weight: bold;
  font-size: 0.85rem;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  backdrop-filter: blur(6px);
}

.create-pill {
  background: rgba(0, 242, 254, 0.2);
  border-color: #00f2fe;
  color: #00f2fe;
}
.create-pill:hover {
  background: #00f2fe;
  color: #000;
  box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
}

.edit-pill {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}
.edit-pill:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
}

.logout-pill {
  background: rgba(214, 48, 49, 0.2);
  border-color: #ff7675;
  color: #ff7675;
}
.logout-pill:hover {
  background: #d63031;
  color: #fff;
  box-shadow: 0 0 15px rgba(214, 48, 49, 0.4);
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

.delete-btn-card {
  background: rgba(214, 48, 49, 0.2);
  border-color: rgba(255, 118, 117, 0.5);
  color: #ff7675;
}
.delete-btn-card:hover {
  background: #d63031;
  color: #fff;
  border-color: #d63031;
}

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
.username-error-text {
  color: #ff4d4d;
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0;
}
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

/* Clickable Location Link Styling */
.clickable-location {
  cursor: pointer;
  color: #00f2fe;
  transition: opacity 0.2s;
  display: inline-block;
}
.clickable-location:hover {
  text-decoration: underline;
  opacity: 0.85;
}

/* Larger Map Modal Styling */
.map-modal-card {
  background: rgba(20, 20, 30, 0.95) !important;
  border: 1px solid rgba(0, 242, 254, 0.4) !important;
  width: 700px !important;
  max-width: 95% !important;
  border-radius: 20px !important;
}
.map-modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.map-popup-wrapper {
  width: 100%;
  height: 480px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.map-iframe-popup {
  width: 100%;
  height: 100%;
  filter: invert(90%) hue-rotate(180deg) contrast(80%);
}

.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.tab-icon {
  width: 18px;
  height: 18px;
  stroke: currentColor;
  transition: transform 0.2s ease, stroke 0.2s ease;
}

.tab:hover .tab-icon {
  transform: scale(1.1);
}

.tab.active .tab-icon {
  stroke: #00f2fe;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.menu-svg-icon {
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.7);
  transition: color 0.2s ease, transform 0.2s ease;
}

.menu-item:hover .menu-svg-icon {
  color: #00f2fe;
  transform: scale(1.1);
}

/* --- UI Icons Layout --- */
.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.ui-icon {
  color: #00f2fe; /* Cyan accent color */
  flex-shrink: 0;
}

.metric-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00f2fe;
}

.delete-btn-card {
  color: #ff4d4d !important;
  border-color: rgba(255, 77, 77, 0.3) !important;
}

.delete-btn-card:hover {
  background: rgba(255, 77, 77, 0.2) !important;
  border-color: #ff4d4d !important;
  color: white !important;
}

</style>
