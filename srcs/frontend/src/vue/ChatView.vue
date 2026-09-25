<script setup>
import { ref } from 'vue';

// Mock contacts list
const contacts = ref([
  { id: 1, name: 'Xhul', img: 'https://i.pravatar.cc/150?u=1', lastMsg: 'Yo bro!' },
  { id: 2, name: 'Anna', img: 'https://i.pravatar.cc/150?u=2', lastMsg: 'Are we still going?' },
  { id: 3, name: 'thilina', img: 'https://i.pravatar.cc/150?u=3', lastMsg: 'Send me the link.' }
]);

// Active chat mock data
const activeChat = ref('Xhul');
const newMessage = ref('');
const messages = ref([
  { id: 1, sender: 'Xhul', text: 'The drop on that first track was insanity!', isMe: false },
  { id: 2, sender: 'Me', text: 'I know right! Best set of the year.', isMe: true },
]);

const sendMessage = () => {
  if (newMessage.value.trim() !== '') {
    messages.value.push({
      id: Date.now(),
      sender: 'Me',
      text: newMessage.value,
      isMe: true
    });
    newMessage.value = '';
  }
};
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
          <li v-for="contact in contacts" :key="contact.id" class="contact-item" :class="{ active: activeChat === contact.name }" @click="activeChat = contact.name">
            <img :src="contact.img" alt="avatar" class="avatar">
            <div class="contact-info">
              <span class="contact-name">{{ contact.name }}</span>
              <span class="contact-last-msg">{{ contact.lastMsg }}</span>
            </div>
          </li>
        </ul>
      </aside>

      <!-- Center: Active Chat Area -->
      <main class="chat-container glass-panel">
        <div class="chat-header">
          <h2>{{ activeChat }}</h2>
        </div>

        <div class="chat-messages">
          <div v-for="msg in messages" :key="msg.id" class="message-wrapper" :class="{ 'my-message': msg.isMe }">
            <div class="message-bubble">
              {{ msg.text }}
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
  color: #FFFFFF; font-family: sans-serif;
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
.contact-info { display: flex; flex-direction: column; }
.contact-name { font-weight: bold; font-size: 1rem; }
.contact-last-msg { font-size: 0.8rem; color: #cccccc; margin-top: 4px; }

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
