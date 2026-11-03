<script setup>
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import SearchBar from './SearchBar.vue';
import EventMediaGrid from './EventMediaGrid.vue';

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
    <header class="navbar glass-panel">
      <div class="logo" @click="router.push('/home')">
        <img src="../assets/logo_temp.png" alt="Ready2Roll Logo" class="nav-logo-img">
        <span class="logo-text">Ready2Roll</span>
      </div>
      <SearchBar />
      <div class="nav-icons">
        <router-link to="/chat" class="nav-icon-link" title="Chat">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 011.037-.443 48.282 48.282 0 005.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" /></svg>
        </router-link>
        <router-link to="/profile" class="nav-icon-link" title="Profile">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>
        </router-link>
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
          <h3 class="section-title">👤 Users ({{ users.length }})</h3>
          <div class="users-grid">
            <router-link
              v-for="u in users"
              :key="u.id"
              :to="{ name: 'UserProfile', params: { id: u.id } }"
              class="user-card glass-panel"
            >
              <img :src="u.avatar" alt="" class="user-avatar">
              <div class="user-text">
                <strong>{{ u.display_name }} <span v-if="u.is_business">💼</span><span v-if="u.is_verified">✔️</span></strong>
                <small>@{{ u.username }}</small>
                <p v-if="u.bio">{{ u.bio }}</p>
              </div>
            </router-link>
          </div>
        </section>

        <section v-if="events.length">
          <h3 class="section-title">🎬 Events ({{ events.length }})</h3>
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
.navbar { display: flex; justify-content: space-between; align-items: center; height: 60px; margin-bottom: 15px; flex-shrink: 0; border: 1px solid rgba(255, 255, 255, 0.15); }
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
.section-title { margin: 0 0 12px; }
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
