<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { useSocialSocket } from '../composables/useSocialSocket';
import { t as $t } from '../i18n';
import { currentLang } from '../i18n';

// Campanellino con pallino rosso + pannello con le notifiche.
// Ogni 20 secondi chiede al backend QUANTE notifiche non lette ci sono (chiamata leggerissima);
// l'elenco completo viene caricato solo quando apri il pannello.
const API = '/api';
const POLL_MS = 20000;
const router = useRouter();

const getToken = () =>
  sessionStorage.getItem('token') || sessionStorage.getItem('access') || sessionStorage.getItem('access_token');
const authHeaders = () => ({ Authorization: `Bearer ${getToken()}` });

const root = ref(null);
const open = ref(false);
const unread = ref(0);
const items = ref([]);
const loading = ref(false);
let timer = null;

// force=true: used for live updates and when the tab becomes visible again.
// Only the periodic polling skips hidden tabs, to spare the server.
const fetchUnread = async (force = false) => {
  if (!getToken() || (document.hidden && !force)) return;
  try {
    const res = await fetch(`${API}/notifications/unread-count/`, { headers: authHeaders() });
    if (res.ok) unread.value = (await res.json()).count;
  } catch (e) { /* rete assente: riprovo al prossimo giro */ }
};

const translateNotification = (text) => {
  if (!text) return '';
  const lowerText = text.toLowerCase();

  if (lowerText.includes('following')) return $t('notifFollow');
  if (lowerText.includes('liked')) return $t('notifLike');
  if (lowerText.includes('commented')) return $t('notifComment');
  if (lowerText.includes('replied')) return $t('notifReply');
  if (lowerText.includes('reacted')) return $t('notificationReacted');

  return text; // Ila kant chi notif khra, tl3 kima hya
};

const loadList = async () => {
  loading.value = true;
  try {
    const res = await fetch(`${API}/notifications/`, { headers: authHeaders() });
    if (res.ok) {
      const data = await res.json();
      items.value = data.results;
      unread.value = data.unread_count;
    }
  } catch (e) { /* ignoro */ } finally {
    loading.value = false;
  }
};

const markAllRead = async () => {
  if (!unread.value) return;
  try {
    const res = await fetch(`${API}/notifications/read/`, { method: 'POST', headers: authHeaders() });
    if (res.ok) unread.value = 0;      // le righe restano evidenziate finche' il pannello e' aperto
  } catch (e) { /* ignoro */ }
};

const toggle = async () => {
  open.value = !open.value;
  if (open.value) {
    await loadList();
    markAllRead();
  }
};

// Click su una notifica -> profilo di chi ha compiuto l'azione
const openNotification = (n) => {
  open.value = false;
  if (n.sender) router.push({ name: 'UserProfile', params: { id: n.sender.id } });
};

const timeAgo = (iso) => {
  const s = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return 'now';
  if (s < 3600) return `${Math.floor(s / 60)}m`;
  if (s < 86400) return `${Math.floor(s / 3600)}h`;
  return `${Math.floor(s / 86400)}d`;
};

// Click fuori dal pannello -> si chiude
const onDocClick = (e) => {
  if (open.value && root.value && !root.value.contains(e.target)) open.value = false;
};

// The server tells us instantly when a notification is created or removed.
// The polling above stays as a safety net (e.g. if the socket is down).
useSocialSocket((message) => {
  if (message.action !== 'notification' && message.action !== 'resync') return;
  if (open.value) loadList();   // panel open: refresh the list too
  else fetchUnread(true);
});

// A hidden or covered tab may have missed updates: catch up as soon as it is visible
const onVisibilityChange = () => {
  if (!document.hidden) fetchUnread(true);
};

onMounted(() => {
  fetchUnread();
  timer = setInterval(() => fetchUnread(), POLL_MS);
  document.addEventListener('click', onDocClick);
  document.addEventListener('visibilitychange', onVisibilityChange);
});
onBeforeUnmount(() => {
  clearInterval(timer);
  document.removeEventListener('click', onDocClick);
  document.removeEventListener('visibilitychange', onVisibilityChange);
});
</script>

<template>
  <div class="bell-root" ref="root">
    <button class="bell-btn" @click="toggle" title="Notifications" aria-label="Notifications">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon"><path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" /></svg>
      <span v-if="unread > 0" class="badge">{{ unread > 9 ? '9+' : unread }}</span>
    </button>

    <div v-if="open" class="panel">
      <div class="panel-head">{{ $t('notificationsTitle') }}</div>

      <p v-if="loading && !items.length" class="empty">Loading...</p>
      <p v-else-if="!items.length" class="empty">{{ $t('noNotificationsYet') }}</p>

      <ul v-else class="list">
        <li v-for="n in items" :key="n.id" :class="{ unread: !n.is_read }" @click="openNotification(n)">
          <img v-if="n.sender" :src="n.sender.avatar" alt="" class="avatar">
          <span v-else class="avatar avatar-system">🔔</span>
          <div class="txt">
            <span><strong>{{ n.sender ? n.sender.username : 'Ready2Roll' }}</strong> {{ translateNotification(n.text) }} </span>
            <small>{{ timeAgo(n.created_at) }}</small>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.bell-root { position: relative; display: flex; align-items: center; }
.bell-btn { position: relative; background: none; border: none; padding: 0; cursor: pointer; color: #fff; display: flex; align-items: center; }
.nav-icon { width: 26px; height: 26px; color: #FFFFFF; transition: all 0.3s ease; }
.bell-btn:hover .nav-icon { color: #00f2fe; transform: scale(1.15); }
.badge {
  position: absolute; top: -6px; right: -8px; min-width: 18px; height: 18px; padding: 0 4px; box-sizing: border-box;
  border-radius: 9px; background: #ff3b5c; color: #fff; font-size: 11px; font-weight: bold;
  display: flex; align-items: center; justify-content: center; box-shadow: 0 0 8px rgba(255, 59, 92, 0.7);
}

.panel {
  position: absolute; top: 42px; right: 0; width: 340px; max-width: calc(100vw - 30px); max-height: 420px; overflow-y: auto;
  background: rgba(20, 10, 40, 0.94); border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 15px;
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5); z-index: 60; color: #fff; text-align: left;
  scrollbar-width: thin; scrollbar-color: rgba(255, 255, 255, 0.25) transparent;
}
.panel-head { padding: 14px 16px; font-family: "Bruno Ace", sans-serif; font-size: 0.95rem; border-bottom: 1px solid rgba(255, 255, 255, 0.12); }
.empty { margin: 0; padding: 24px 16px; text-align: center; color: rgba(255, 255, 255, 0.6); font-size: 0.9rem; }
.list { list-style: none; margin: 0; padding: 6px; }
.list li { display: flex; align-items: flex-start; gap: 10px; padding: 10px; border-radius: 10px; cursor: pointer; transition: background 0.2s ease; margin: 0; }
.list li:hover { background: rgba(255, 255, 255, 0.08); }
.list li.unread { background: rgba(0, 242, 254, 0.12); }
.avatar { width: 38px; height: 38px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.avatar-system { display: flex; align-items: center; justify-content: center; background: rgba(255, 255, 255, 0.12); }
.txt { display: flex; flex-direction: column; gap: 3px; min-width: 0; font-size: 0.85rem; line-height: 1.35; word-break: break-word; }
.txt small { color: rgba(255, 255, 255, 0.55); font-size: 0.75rem; }
</style>
