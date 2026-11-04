<script setup>
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import SearchBar from './SearchBar.vue';
import EventMediaGrid from './EventMediaGrid.vue';
import NotificationBell from './NotificationBell.vue';

const API = '/api';
const route = useRoute();
const router = useRouter();

const getToken = () =>
  localStorage.getItem('token') || localStorage.getItem('access') || localStorage.getItem('access_token');

const query = ref('');
const users = ref([]);
const events = ref([]);
const loading = ref(false);
const error = ref('');

let lastRequest = 0;   // evita che una risposta vecchia sovrascriva una piu' recente

const runSearch = async (q) => {
  query.value = q;
  users.value = [];
  events.value = [];
  error.value = '';
  if (!q) return;

  const myRequest = ++lastRequest;
  loading.value = true;
  try {
    const res = await fetch(`${API}/search/?q=${encodeURIComponent(q)}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (res.status === 401) { router.push('/login'); return; }
    if (!res.ok) throw new Error('bad status');
    const data = await res.json();
    if (myRequest !== lastRequest) return;
    users.value = data.users || [];
    events.value = data.events || [];
  } catch (e) {
    if (myRequest === lastRequest) error.value = 'Could not load the results. Try again.';
  } finally {
    if (myRequest === lastRequest) loading.value = false;
  }
};

// Si riesegue ogni volta che cambia ?q=... (anche alla prima apertura)
watch(() => route.query.q, (q) => runSearch(String(q || '').trim()), { immediate: true });
</script>

<template>
  <video autoplay muted loop playsinline id="bgVideo">
    <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
  </video>

  <div class="app-container">
    <!-- Navbar (M9adda b7al Home/Profile) -->
    <header class="navbar glass-panel">
      <div class="nav-left">
        <div class="logo" @click="router.push('/home')">
          <img src="../assets/logo_temp.png" alt="Ready2Roll Logo" class="nav-logo-img">
          <span class="logo-text">Ready2Roll</span>
        </div>
      </div>

      <!-- Search Bar Component -->
      <SearchBar />

      <div class="nav-right">
        <div class="nav-icons">
          <!-- Direct Messages Icon -->
          <router-link to="/direct" class="nav-icon-link" title="Direct Messages">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="nav-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
          </router-link>

          <!-- Chat Icon -->
          <router-link to="/chat" class="nav-icon-link" title="Chat">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="nav-icon">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a.75.75 0 01-.81-.54 2.89 2.89 0 01.213-1.637 8.25 8.25 0 01-1.813-5.293C3 7.444 7.03 3.75 12 3.75s9 3.694 9 8.25z" />
             </svg>
          </router-link>

          <!-- Profile Icon -->
          <router-link to="/profile" class="nav-icon-link" title="Profile">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="nav-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
            </svg>
          </router-link>
        </div>
      </div>
    </header>

    <main class="results-container">
      <h2 v-if="query" class="results-title">Results for “{{ query }}”</h2>

      <p v-if="!query" class="state-msg glass-panel">Type a name, an event or a tag in the search bar.</p>
      <p v-else-if="loading" class="state-msg glass-panel">Searching...</p>
      <p v-else-if="error" class="state-msg glass-panel">{{ error }}</p>
      <p v-else-if="!users.length && !events.length" class="state-msg glass-panel">
        Nothing found for “{{ query }}”. Try another name, event or tag.
      </p>

      <template v-else>
        <section v-if="users.length">
          <h3 class="section-title">
             <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-users ui-icon"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><path d="M16 3.128a4 4 0 0 1 0 7.744"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><circle cx="9" cy="7" r="4"/></svg>
             Users ({{ users.length }})
          </h3>
          <div class="users-grid">
            <router-link
              v-for="u in users"
              :key="u.id"
              :to="{ name: 'UserProfile', params: { id: u.id } }"
              class="user-card glass-panel"
            >
              <img :src="u.avatar" alt="" class="user-avatar">
              <div class="user-text">
                <strong style="display: flex; align-items: center; gap: 4px;">
                   {{ u.display_name }}
                   <svg v-if="u.is_business" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="#00f2fe" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="verified-badge"><path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"/><path d="m16 9-5.5 5.5L8 12" stroke="#ffffff" stroke-width="2.5"/></svg>
                </strong>
                <small>@{{ u.username }}</small>
                <p v-if="u.bio">{{ u.bio }}</p>
              </div>
            </router-link>
          </div>
        </section>

        <section v-if="events.length">
          <h3 class="section-title">
             <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calendar-days ui-icon"><path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M8 13h.01"/><path d="M12 13h.01"/><path d="M16 13h.01"/><path d="M8 17h.01"/><path d="M12 17h.01"/><path d="M16 17h.01"/></svg>
             Events ({{ events.length }})
          </h3>
          <!-- Event Grid Component -->
          <EventMediaGrid :events="events" />
        </section>
      </template>
    </main>
  </div>
</template>

<style scoped>
#bgVideo { position: fixed; top: 0; left: 0; right: 0; bottom: 0; width: 100%; height: 100%; z-index: -1; object-fit: cover; }
.app-container { display: flex; flex-direction: column; height: 100vh; color: #FFFFFF; font-family: sans-serif; padding: 10px 20px; box-sizing: border-box; }
.glass-panel { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; box-sizing: border-box; }

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  margin-bottom: 15px;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.15);
  width: 100%; /* Hadi katkhlliha tchd l'3erd kaml */
  box-sizing: border-box;
}

.nav-left, .nav-right { display: flex; align-items: center; flex: 1; }
.nav-right { justify-content: flex-end; }

.logo { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.nav-logo-img { height: 35px; width: auto; object-fit: contain; }
.logo-text { font-family: "Bruno Ace", sans-serif; font-weight: bold; font-size: 1.2rem; }
.nav-icons { display: flex; gap: 20px; align-items: center; }
.nav-icon { width: 26px; height: 26px; color: #FFFFFF; cursor: pointer; transition: all 0.3s ease; }
.nav-icon:hover { color: #00f2fe; transform: scale(1.15); }
.nav-icon-link { display: flex; align-items: center; }

.results-container { flex: 1; min-height: 0; overflow-y: auto; scrollbar-width: none; display: flex; flex-direction: column; gap: 20px; width: 100%; max-width: 1100px; margin: 0 auto; }
.results-container::-webkit-scrollbar { display: none; }
.results-title { margin: 0; font-family: "Bruno Ace", sans-serif; font-size: 1.3rem; }

.section-title { margin: 0 0 12px; display: flex; align-items: center; gap: 8px; }
.ui-icon { color: #00f2fe; }

.state-msg { text-align: center; color: #cfcfcf; margin: 0; }

.users-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; }
.user-card { display: flex; align-items: center; gap: 12px; text-decoration: none; color: white; border: 1px solid rgba(255, 255, 255, 0.15); transition: transform 0.2s ease, border-color 0.2s ease; }
.user-card:hover { transform: translateY(-3px); border-color: rgba(0, 242, 254, 0.6); }
.user-avatar { width: 52px; height: 52px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.user-text { min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.user-text strong { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-text small { color: rgba(255, 255, 255, 0.65); }
.user-text p { margin: 4px 0 0; font-size: 0.8rem; color: rgba(255, 255, 255, 0.75); display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>
