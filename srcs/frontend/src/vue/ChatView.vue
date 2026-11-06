<!-- file: ChatView.vue -->
<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';

const contacts = ref([]);          // Contatti con chat attive
const searchResults = ref([]);     // Risultati della ricerca globale
const activeContact = ref(null);
const messages = ref([]);
const newMessage = ref('');
let socket = null;
let pollTimer = null;
const searchQuery = ref('');

// Cerca nel database quando l'utente digita nella search bar
watch(searchQuery, async (newQuery) => {
  if (!newQuery || !newQuery.trim()) {
    searchResults.value = [];
    return;
  }
  const token = getToken();
  try {
    const res = await fetch(`/api/social/users/search/?q=${encodeURIComponent(newQuery.trim())}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) {
      const data = await res.json();
      // Escludiamo l'admin dai risultati della ricerca
      const filteredData = data.filter(u => u.username?.toLowerCase() !== 'admin' && u.email?.toLowerCase() !== 'admin');
      
      searchResults.value = filteredData.map(u => ({
        id: u.id,
        name: u.username,
        img: u.avatar_url ? (u.avatar_url.startsWith('http') ? u.avatar_url : `http://localhost:9000/media/${u.avatar_url}`) : 'https://i.pravatar.cc/150?u=' + u.id,
        lastMsg: 'Click to start chatting',
        lastMsgAt: null,
        unread: 0
      }));
    } else {
      searchResults.value = [];
    }
  } catch (err) {
    console.error('Error searching users:', err);
    searchResults.value = [];
  }
});

// ---- time helpers ----
const formatTime = (iso) => {
  if (!iso) return '';
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const formatContactTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  const now = new Date();
  if (d.toDateString() === now.toDateString()) return formatTime(iso);
  return d.toLocaleDateString([], { day: '2-digit', month: '2-digit' });
};

const sortContacts = () => {
  contacts.value.sort((a, b) => {
    if (a.lastMsgAt && b.lastMsgAt) return new Date(b.lastMsgAt) - new Date(a.lastMsgAt);
    if (a.lastMsgAt) return -1;
    if (b.lastMsgAt) return 1;
    return a.name.localeCompare(b.name);
  });
};

const getToken = () =>
  localStorage.getItem('token') ||
  localStorage.getItem('access') ||
  localStorage.getItem('access_token');

// Fetch contacts attivi
const fetchContacts = async () => {
  const token = getToken();
  try {
    const res = await fetch('/api/social/contacts/', {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) {
      const data = await res.json();
      contacts.value = data.map(u => ({
        id: u.id,
        name: u.username,
        img: u.avatar_url ? (u.avatar_url.startsWith('http') ? u.avatar_url : `http://localhost:9000/media/${u.avatar_url}`) : 'https://i.pravatar.cc/150?u=' + u.id,
        lastMsg: u.lastMsg || '',
        lastMsgAt: u.lastMsgAt || null,
        unread: u.unread || 0
      }));

      const open = contacts.value.find(c => c.id === activeContact.value?.id);
      if (open) open.unread = 0;

      sortContacts();
    }
  } catch (error) {
    console.error('Error fetching contacts:', error);
  }
};

// Seleziona un contatto dalla ricerca o dalla lista e pulisce la ricerca
const selectContact = async (contact) => {
  activeContact.value = contact;
  contact.unread = 0;
  searchQuery.value = ''; // Pulisce la barra di ricerca quando si seleziona un utente
  searchResults.value = [];

  if (socket) {
    socket.close();
  }

  const token = getToken();
  const res = await fetch(`/api/social/messages/${contact.id}/`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (res.ok) {
    messages.value = await res.json();
  }
  fetchContacts();

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/chat/${contact.id}/?token=${token}`;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log("✅ WebSocket Connected!");
  };

  socket.onmessage = (event) => {
    const incomingMsg = JSON.parse(event.data);
    messages.value.push(incomingMsg);

    const c = contacts.value.find(x => x.id === activeContact.value?.id);
    if (c) {
      c.lastMsg = (incomingMsg.isMe ? 'You: ' : '') + incomingMsg.text;
      c.lastMsgAt = incomingMsg.created_at;
      c.unread = 0;
      sortContacts();
    } else {
      fetchContacts();
    }
  };

  socket.onerror = (error) => {
    console.error("❌ WebSocket Error:", error);
  };

  socket.onclose = (event) => {
    console.log("🔌 WebSocket Closed. Code:", event.code);
  };
};

const sendMessage = () => {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    alert("Cannot send: The live chat connection dropped!");
    return;
  }

  if (newMessage.value.trim() !== '') {
    socket.send(JSON.stringify({ text: newMessage.value }));
    newMessage.value = '';
    setTimeout(fetchContacts, 500);
  }
};

onMounted(() => {
  fetchContacts();
  pollTimer = setInterval(fetchContacts, 3000);
});

onBeforeUnmount(() => {
  if (socket) socket.close();
  if (pollTimer) clearInterval(pollTimer);
});
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
      <div class="nav-icons">
        <router-link to="/home" class="nav-icon-link">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
          </svg>
        </router-link>
      </div>
    </header>

    <div class="main-content">
      <aside class="left-sidebar glass-panel">
        <div class="sidebar-search-bar">
          <input type="text" v-model="searchQuery" placeholder="Search users to chat..." autocomplete="off">
        </div>
        
        <h3>Messages</h3>

        <!-- Risultati della ricerca globale -->
        <ul v-if="searchQuery.trim()">
          <p class="search-label">Global Search:</p>
          <li v-for="contact in searchResults" :key="contact.id" class="contact-item"
            :class="{ active: activeContact?.id === contact.id }"
            @click="selectContact(contact)">
            <img :src="contact.img" alt="avatar" class="avatar">
            <div class="contact-info">
              <span class="contact-name">{{ contact.name }}</span>
              <span class="contact-last-msg">Click to message</span>
            </div>
          </li>
          <li v-if="searchResults.length === 0" class="no-results">No users found.</li>
        </ul>

        <!-- Lista dei contatti attivi -->
        <ul v-else>
          <li v-for="contact in contacts" :key="contact.id" class="contact-item"
            :class="{ active: activeContact?.id === contact.id }"
            @click="selectContact(contact)">
            <img :src="contact.img" alt="avatar" class="avatar">
            <div class="contact-info">
              <span class="contact-name">{{ contact.name }}</span>
              <span class="contact-last-msg" :class="{ 'has-unread': contact.unread > 0 && activeContact?.id !== contact.id }">{{ contact.lastMsg }}</span>
            </div>
            <div class="contact-meta">
              <span class="contact-time">{{ formatContactTime(contact.lastMsgAt) }}</span>
              <span v-if="contact.unread > 0 && activeContact?.id !== contact.id" class="unread-dot"></span>
            </div>
          </li>
          <li v-if="contacts.length === 0" class="no-results">No active chats yet. Use search above!</li>
        </ul>
      </aside>

      <main class="chat-container glass-panel">
        <div class="chat-header">
          <h2 v-if="activeContact">{{ activeContact.name }}</h2>
          <h2 v-else>Select a contact</h2>
        </div>

        <div class="chat-messages">
          <div v-for="msg in messages" :key="msg.id" class="message-wrapper" :class="{ 'my-message': msg.isMe }">
            <div class="message-bubble">
              <span class="message-text">{{ msg.text }}</span>
              <span class="message-time">{{ formatTime(msg.created_at) }}</span>
            </div>
          </div>
        </div>

        <form class="chat-input-area" @submit.prevent="sendMessage">
          <input type="text" v-model="newMessage" placeholder="Type a message..." required>
          <button type="submit">Send</button>
        </form>
      </main>
    </div>
  </div>
</template>

<style scoped>
#bgVideo {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    width: 100%; height: 100%; z-index: -1; object-fit: cover;
}
.app-container {
  display: flex; flex-direction: column; height: 100vh;
  color: #FFFFFF; font-family: sans-serif;
  padding: 10px 20px; box-sizing: border-box;
}
.glass-panel {
  background: rgba(255, 255, 255, 0.1); border-radius: 15px;
  padding: 15px; box-sizing: border-box;
}
.navbar {
  display: flex; justify-content: space-between; align-items: center;
  height: 60px; margin-bottom: 15px; flex-shrink: 0;
}
.logo { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.nav-logo-img { height: 35px; width: auto; object-fit: contain; }
.logo-text { font-family: "Bruno Ace", sans-serif; font-weight: bold; font-size: 1.2rem; }
.nav-icons { display: flex; gap: 20px; align-items: center; }
.nav-icon { width: 26px; height: 26px; color: #FFFFFF; cursor: pointer; transition: all 0.3s ease; }
.nav-icon:hover { color: #00f2fe; transform: scale(1.15); }
.nav-icon-link { display: flex; align-items: center; }
.main-content {
  display: flex; flex-direction: row; gap: 15px;
  height: calc(100vh - 95px); width: 100%;
}
.left-sidebar {
  width: 300px; display: flex; flex-direction: column; gap: 15px; overflow-y: auto;
}
.sidebar-search-bar input {
  width: 100%; box-sizing: border-box;
  background: rgba(255, 255, 255, 0.1); border: none;
  border-radius: 17px; padding: 10px 15px; color: white; outline: none;
  transition: background 0.2s ease;
}
.sidebar-search-bar input:focus { background: rgba(255, 255, 255, 0.18); }
.search-label { font-size: 0.75rem; color: #00f2fe; margin-bottom: 8px; font-weight: bold; text-transform: uppercase; }
.no-results { font-size: 0.85rem; color: #cccccc; text-align: center; padding: 15px 0; }
ul { list-style: none; padding: 0; margin: 0; }
.contact-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px; border-radius: 10px; cursor: pointer; transition: background 0.2s;
}
.contact-item:hover, .contact-item.active { background: rgba(255, 255, 255, 0.2); }
.avatar { width: 45px; height: 45px; border-radius: 50%; object-fit: cover; }
.contact-info { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.contact-name { font-weight: bold; font-size: 1rem; }
.contact-last-msg {
  font-size: 0.8rem; color: #cccccc; margin-top: 4px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.contact-last-msg.has-unread { color: #FFFFFF; font-weight: bold; }
.contact-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }
.contact-time { font-size: 0.7rem; color: #cccccc; }
.unread-dot { width: 10px; height: 10px; border-radius: 50%; background: #00f2fe; box-shadow: 0 0 6px #00f2fe; }
.chat-container { flex-grow: 1; display: flex; flex-direction: column; }
.chat-header { padding-bottom: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.2); margin-bottom: 15px; }
.chat-header h2 { margin: 0; font-family: "Bruno Ace", sans-serif; }
.chat-messages { flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; padding-right: 10px; }
.message-wrapper { display: flex; width: 100%; }
.my-message { justify-content: flex-end; }
.message-bubble {
  max-width: 60%; padding: 12px 18px; border-radius: 20px;
  background: rgba(255, 255, 255, 0.15); line-height: 1.4;
}
.my-message .message-bubble { background: rgba(0, 242, 254, 0.3); border-bottom-right-radius: 4px; }
.message-text { white-space: pre-wrap; word-break: break-word; }
.message-time { display: block; text-align: right; margin-top: 4px; font-size: 0.7rem; color: rgba(255, 255, 255, 0.65); }
.message-wrapper:not(.my-message) .message-bubble { border-bottom-left-radius: 4px; }
.chat-input-area {
  display: flex; gap: 10px; margin-top: 15px; padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}
.chat-input-area input {
  flex-grow: 1; background: rgba(255, 255, 255, 0.1); border: none;
  border-radius: 20px; padding: 12px 20px; color: white;
}
.chat-input-area input::placeholder { color: #cccccc; }
.chat-input-area button {
  background: #00d2d3; color: white; border: none; border-radius: 20px;
  padding: 0 25px; cursor: pointer; font-weight: bold; transition: background 0.3s;
}
.chat-input-area button:hover { background: #00f2fe; }
</style>