<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const contacts = ref([]);
const activeContact = ref(null);
const messages = ref([]);
const newMessage = ref('');
let socket = null;
let pollTimer = null;

// ---- time helpers ----
const formatTime = (iso) => {
  if (!iso) return '';
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// Sidebar: hour if today, otherwise a short date
const formatContactTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  const now = new Date();
  if (d.toDateString() === now.toDateString()) return formatTime(iso);
  return d.toLocaleDateString([], { day: '2-digit', month: '2-digit' });
};

// Latest conversation first (contacts without messages stay at the bottom)
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

// 1. Fetch contacts when the page loads
const fetchContacts = async () => {
  const token = getToken();
  try {
    const res = await fetch('/api/social/contacts/', {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) {
      contacts.value = await res.json();
      // the chat that is open is already read
      const open = contacts.value.find(c => c.id === activeContact.value?.id);
      if (open) open.unread = 0;
    }
  } catch (error) {
    console.error('Error fetching contacts:', error);
  }
};

// 2. Open a DM and connect the WebSocket
const selectContact = async (contact) => {
  activeContact.value = contact;
  contact.unread = 0;   // opening the chat removes the dot

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
  fetchContacts();   // the history request marked the messages as read

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/chat/${contact.id}/?token=${token}`;

  console.log("Attempting to connect to:", wsUrl);
  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log("✅ WebSocket Connected!");
  };

  socket.onmessage = (event) => {
    const incomingMsg = JSON.parse(event.data);
    messages.value.push(incomingMsg);

    // Update the sidebar: last message + move this conversation to the top
    const c = contacts.value.find(x => x.id === activeContact.value?.id);
    if (c) {
      c.lastMsg = (incomingMsg.isMe ? 'You: ' : '') + incomingMsg.text;
      c.lastMsgAt = incomingMsg.created_at;
      c.unread = 0;
      sortContacts();
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
  // Check if socket is open
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    alert("Cannot send: The live chat connection dropped! (State: " + (socket ? socket.readyState : 'null') + ")");
    return;
  }

  if (newMessage.value.trim() !== '') {
    socket.send(JSON.stringify({ text: newMessage.value }));
    newMessage.value = '';
  }
};

onMounted(() => {
  fetchContacts(); // Fire the fetch on load!
  // Refresh the list so new messages from other contacts show up (dot + order)
  pollTimer = setInterval(fetchContacts, 3000);
});

onBeforeUnmount(() => {
  if (socket) socket.close();
  if (pollTimer) clearInterval(pollTimer);
});
</script>

<template>
  <!-- Background Video -->
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
        <input type="text" placeholder="Search chats...">
      </div>
      <div class="nav-icons">
        <router-link to="/home" class="nav-icon-link">
          <!-- Home Icon to go back -->
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
          </svg>
        </router-link>
      </div>
    </header>

    <div class="main-content">
      <!-- Left Sidebar: Contacts -->
      <aside class="left-sidebar glass-panel">
        <h3>Messages</h3>
        <ul>
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
        </ul>
      </aside>

      <!-- Center: Active Chat Area -->
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
/* Core layout styles retained from HomeView */
#bgVideo {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    width: 100%; height: 100%; z-index: -1; object-fit: cover;
}
.app-container {
  display: flex; flex-direction: column; height: 100vh;
  color: #FFFFFF; font-family: var(--font-main);
  padding: 10px 20px; box-sizing: border-box;
}
.glass-panel {
  background: rgba(255, 255, 255, 0.1); border-radius: 15px;
  padding: 15px; box-sizing: border-box;
}

/* Navbar */
.navbar {
  display: flex; justify-content: space-between; align-items: center;
  height: 60px; margin-bottom: 15px; flex-shrink: 0;
}
.logo { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.nav-logo-img { height: 35px; width: auto; object-fit: contain; }
.logo-text { font-family: "Bruno Ace", sans-serif; font-weight: bold; font-size: 1.2rem; }
.search-bar input {
  background: rgba(255, 255, 255, 0.1); border: none;
  border-radius: 17px; padding: 10px 20px; color: white; width: 300px;
}
.nav-icons { display: flex; gap: 20px; align-items: center; }
.nav-icon { width: 26px; height: 26px; color: #FFFFFF; cursor: pointer; transition: all 0.3s ease; }
.nav-icon:hover { color: #00f2fe; transform: scale(1.15); }
.nav-icon-link { display: flex; align-items: center; }

/* Main Layout */
.main-content {
  display: flex; flex-direction: row; gap: 15px;
  height: calc(100vh - 95px); width: 100%;
}
.left-sidebar {
  width: 300px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto;
}

/* Contacts List */
ul { list-style: none; padding: 0; margin: 0; }
.contact-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px; border-radius: 10px; cursor: pointer; transition: background 0.2s;
}
.contact-item:hover, .contact-item.active { background: rgba(255, 255, 255, 0.2); }
.avatar { width: 45px; height: 45px; border-radius: 50%; }
.contact-info { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.contact-name { font-weight: bold; font-size: 1rem; }
.contact-last-msg {
  font-size: 0.8rem; color: #cccccc; margin-top: 4px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.contact-last-msg.has-unread { color: #FFFFFF; font-weight: bold; }
.contact-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }
.contact-time { font-size: 0.7rem; color: #cccccc; }
.unread-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: #00f2fe; box-shadow: 0 0 6px #00f2fe;
}

/* Chat Container */
.chat-container {
  flex-grow: 1; display: flex; flex-direction: column;
}
.chat-header {
  padding-bottom: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 15px;
}
.chat-header h2 { margin: 0; font-family: "Bruno Ace", sans-serif; }

/* Messages Area */
.chat-messages {
  flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 15px;
  padding-right: 10px;
}
.message-wrapper { display: flex; width: 100%; }
.my-message { justify-content: flex-end; }
.message-bubble {
  max-width: 60%; padding: 12px 18px; border-radius: 20px;
  background: rgba(255, 255, 255, 0.15); line-height: 1.4;
}
.my-message .message-bubble {
  background: rgba(0, 242, 254, 0.3); border-bottom-right-radius: 4px;
}
.message-text { white-space: pre-wrap; word-break: break-word; }
.message-time {
  display: block; text-align: right; margin-top: 4px;
  font-size: 0.7rem; color: rgba(255, 255, 255, 0.65);
}
.message-wrapper:not(.my-message) .message-bubble { border-bottom-left-radius: 4px; }

/* Input Area */
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
