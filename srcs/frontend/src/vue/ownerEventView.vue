<script>
export default {
name: 'OwnerEventView',
emits: ['navigate-create'],
data() {
return {
activePreviewEvent: null,
isExpanded: false,
isMapOpen: false,
isEditing: false,
editForm: {
id: null,
title: '',
location: '',
event_date: '',
status: 'active',
description: '',
media_type: 'image',
media_src: ''
},
eventsList: []
}
},
async mounted() {
// Automatically fetches all events via GET request when the page loads
await this.fetchOwnerEvents();
},
methods: {
async fetchOwnerEvents() {
try {
const token = localStorage.getItem('token') || localStorage.getItem('access');
const response = await fetch('http://localhost:8000/api/owner/events/', {
method: 'GET', // GET request to retrieve created events from the backend
headers: {
'Authorization': `Bearer ${token}`
}
});

if (response.ok) {
const data = await response.json();
this.eventsList = data; // Populates the grid with events
} else {
console.error("Error fetching events:", await response.json());
}
} catch (error) {
console.error("Connection error while fetching events:", error);
}
},

goToCreateEvent() {
this.$router.push('/CreateEvent');
},

openPreview(event) {
this.activePreviewEvent = event;
this.isExpanded = false;
this.isMapOpen = false;
},
closePreview() {
this.activePreviewEvent = null;
this.isExpanded = false;
this.isMapOpen = false;
},
toggleExpand() {
this.isExpanded = !this.isExpanded;
if (this.isExpanded) this.isMapOpen = false;
},
toggleMap() {
this.isMapOpen = !this.isMapOpen;
if (this.isMapOpen) {
this.selectStep(2);
} else {
this.selectStep(1);
}
},

openEdit(event) {
this.editForm = { ...event };
this.isEditing = true;
},
closeEdit() {
this.isEditing = false;
},

async saveEdit() {
const token = localStorage.getItem('token') || localStorage.getItem('access');
const payload = {
title: this.editForm.title,
location: this.editForm.location,
event_date: this.editForm.event_date,
status: this.editForm.status,
description: this.editForm.description,
media_type: this.editForm.media_type,
media_src: this.editForm.media_src
};

try {
const response = await fetch(`http://localhost:8000/api/events/${this.editForm.id}/`, {
method: 'PUT',
headers: {
'Content-Type': 'application/json',
'Authorization': `Bearer ${token}`
},
body: JSON.stringify(payload)
});

if (response.ok) {
const updatedEvent = await response.json();
const index = this.eventsList.findIndex(e => e.id === this.editForm.id);
if (index !== -1) {
this.eventsList.splice(index, 1, updatedEvent);
}
alert("Event updated successfully!");
this.closeEdit();
} else {
const errData = await response.json();
console.error("Error updating event:", errData);
alert("Error saving changes.");
}
} catch (error) {
console.error("Network error during save:", error);
alert("Unable to connect to the backend server.");
}
},
triggerEditFileInput() {
this.$refs.editFileInput.click();
},
handleEditFileUpload(e) {
const file = e.target.files[0];
if (file) {
this.editForm.media_src = URL.createObjectURL(file);
this.editForm.media_type = file.type.startsWith('video') ? 'video' : 'image';
}
}
}
}
</script>

<template>
<div class="owner-visual-wrapper">
<video autoplay muted loop playsinline id="bgVideo">
<source src="../assets/ready2roll_wave_background.mp4" type="video/mp4" />
</video>

<header class="navbar glass-panel">
<div class="nav-left">
<div class="logo">
<img src="../assets/logo_temp.png" alt="Ready2Roll Logo" class="nav-logo-img" />
<span class="logo-text">Ready2Roll</span>
</div>
</div>

<div class="nav-right">
<div class="nav-icons">
<router-link to="/direct" class="nav-icon-link" title="Messaggi diretti">
<svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
<path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
</svg>
</router-link>
<router-link to="/chat" class="nav-icon-link" title="Chat">
<svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
<path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a.75.75 0 01-.81-.54 2.89 2.89 0 01.213-1.637 8.25 8.25 0 01-1.813-5.293C3 7.444 7.03 3.75 12 3.75s9 3.694 9 8.25z" />
</svg>
</router-link>
<router-link to="/profile" class="nav-icon-link" title="Profilo">
<svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
<path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
</svg>
</router-link>
</div>
</div>
</header>

<main class="main-content">
<div class="page-header">
<h1 class="page-title">MY EVENTS</h1>
<p class="subtitle">Manage, edit, and preview your events in full screen.</p>
<div class="create-event-cta">
<span class="cta-prompt">Not finding your event? Create it now!</span>
<button class="action-btn create-nav-btn" @click="goToCreateEvent">
<span class="btn-icon">
<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
	<line x1="12" y1="5" x2="12" y2="19"></line>
	<line x1="5" y1="12" x2="19" y2="12"></line>
</svg>
</span>
<span>Create new event</span>
</button>
</div>
</div>

<section class="events-grid">
<div
v-for="event in eventsList"
:key="event.id"
class="event-card glass-card"
>
<div class="card-media-header">
<img
v-if="event.media_type === 'image'"
:src="event.media_src"
alt="Cover evento"
class="card-thumb"
/>
<video
v-else
:src="event.media_src"
autoplay
muted
loop
class="card-thumb"
></video>
<span class="status-badge" :class="event.status ? event.status.toLowerCase() : ''">
{{ event.status }}
</span>
</div>

<div class="card-body">
<h3 class="event-title">{{ event.title }}</h3>
<div class="event-info-row">
<span>📍 {{ event.location }}</span>
<span>📅 {{ event.event_date }}</span>
</div>
<p class="event-description-truncated">
{{ event.description || 'No description was inserted' }}
</p>
</div>

<div class="card-actions">
<button class="action-btn preview-btn" @click="openPreview(event)">
👁️ Anteprima
</button>
<button class="action-btn edit-btn" @click="openEdit(event)">
✏️ Modifica
</button>
</div>
</div>
</section>

<!-- Preview & Edit Modals remain unchanged -->
</main>
</div>
</template>

<style scoped>
@import url('https://cdn.jsdelivr.net/gh/justfont/open-huninn-font@1.1/font/jf-openhuninn.css');

.owner-visual-wrapper {
position: relative;
min-height: 100vh;
width: 100%;
color: #ffffff;
font-family: 'jf-openhuninn', 'Huninn', sans-serif;
box-sizing: border-box;
padding-bottom: 50px;
}

.logo,
.logo-text {
font-family: "Bruno Ace", sans-serif !important;
font-weight: bold;
}

#bgVideo {
position: fixed;
top: 0;
left: 0;
right: 0;
bottom: 0;
min-width: 100%;
min-height: 100%;
width: 100%;
height: 100%;
z-index: -1;
object-fit: cover;
}

.navbar {
display: flex;
align-items: center;
justify-content: space-between;
padding: 12px 30px;
width: 100%;
box-sizing: border-box;
background: rgba(255, 255, 255, 0.08);
backdrop-filter: blur(16px);
-webkit-backdrop-filter: blur(16px);
border-bottom: 1px solid rgba(255, 255, 255, 0.15);
position: sticky;
top: 0;
z-index: 1000;
}

.nav-left, .nav-right {
display: flex;
align-items: center;
flex: 1;
}

.nav-right {
justify-content: flex-end;
}

.logo {
display: flex;
align-items: center;
gap: 12px;
cursor: pointer;
}

.nav-logo-img {
width: 32px;
height: 32px;
object-fit: contain;
}

.logo-text {
font-family: 'Bruno Ace', sans-serif !important;
font-size: 1.25rem;
color: #ffffff;
letter-spacing: 0.5px;
}

.nav-icons {
display: flex;
align-items: center;
gap: 20px;
}

.nav-icon-link {
color: rgba(255, 255, 255, 0.85);
display: flex;
align-items: center;
justify-content: center;
text-decoration: none;
transition: color 0.2s ease, transform 0.2s ease;
}

.nav-icon-link:hover {
color: #00f2fe;
transform: translateY(-1px);
}

.nav-icon {
width: 24px;
height: 24px;
}

.main-content {
max-width: 1200px;
margin: 0 auto;
padding: 40px 20px;
box-sizing: border-box;
}

.page-header {
text-align: center;
margin-bottom: 35px;
}

.page-title {
font-size: 2.2rem;
margin: 0;
letter-spacing: 1px;
text-transform: uppercase;
}

.subtitle {
font-size: 0.9rem;
color: rgba(255, 255, 255, 0.7);
margin: 6px 0 0 0;
}

.create-event-cta {
display: flex;
flex-direction: column;
align-items: center;
gap: 12px;
margin-top: 24px;
}

.cta-prompt {
font-size: 0.95rem;
color: rgba(255, 255, 255, 0.9);
letter-spacing: 0.5px;
text-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
}

.create-nav-btn {
display: inline-flex;
align-items: center;
justify-content: center;
gap: 10px;
background: linear-gradient(135deg, rgba(0, 242, 254, 0.2), rgba(0, 150, 255, 0.3));
border: 1px solid rgba(0, 242, 254, 0.7);
color: #ffffff;
padding: 12px 26px;
font-size: 0.85rem;
font-weight: bold;
border-radius: 50px;
backdrop-filter: blur(12px);
box-shadow: 0 0 16px rgba(0, 242, 254, 0.25), inset 0 0 10px rgba(0, 242, 254, 0.15);
cursor: pointer;
transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
letter-spacing: 0.5px;
user-select: none;
}

.create-nav-btn:hover {
background: #00f2fe;
color: #000000;
box-shadow: 0 0 20px rgba(0, 242, 254, 0.7);
transform: translateY(-2px);
}

.events-grid {
display: grid;
grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
gap: 28px;
width: 100%;
}

.glass-card {
background: rgba(255, 255, 255, 0.08);
border-radius: 20px;
padding: 18px;
box-sizing: border-box;
backdrop-filter: blur(12px);
border: 1px solid rgba(255, 255, 255, 0.18);
transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

.event-card:hover {
transform: translateY(-5px);
border-color: rgba(0, 242, 254, 0.6);
box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
}

.card-media-header {
position: relative;
width: 100%;
height: 180px;
border-radius: 14px;
overflow: hidden;
margin-bottom: 15px;
}

.card-thumb {
width: 100%;
height: 100%;
object-fit: cover;
}

.status-badge {
position: absolute;
top: 10px;
right: 10px;
padding: 4px 10px;
border-radius: 10px;
font-size: 0.7rem;
font-weight: bold;
backdrop-filter: blur(6px);
text-transform: uppercase;
}

.status-badge.attivo {
background: rgba(0, 242, 254, 0.3);
border: 1px solid #00f2fe;
color: #00f2fe;
}

.status-badge.bozza {
background: rgba(255, 193, 7, 0.3);
border: 1px solid #ffc107;
color: #ffc107;
}

.status-badge.programmato {
background: rgba(156, 39, 176, 0.3);
border: 1px solid #e040fb;
color: #e040fb;
}

.card-body {
margin-bottom: 18px;
}

.event-title {
font-size: 1.1rem;
margin: 0 0 10px 0;
white-space: nowrap;
overflow: hidden;
text-overflow: ellipsis;
}

.event-info-row {
display: flex;
flex-direction: column;
gap: 4px;
font-size: 0.78rem;
color: rgba(255, 255, 255, 0.8);
margin-bottom: 12px;
}

.event-description-truncated {
font-size: 0.8rem;
color: rgba(255, 255, 255, 0.65);
line-height: 1.4;
display: -webkit-box;
-webkit-line-clamp: 2;
line-clamp: 2;
-webkit-box-orient: vertical;
overflow: hidden;
margin: 0;
}

.card-actions {
display: flex;
gap: 10px;
}

.action-btn {
flex: 1;
padding: 10px 12px;
border-radius: 12px;
border: 1px solid rgba(255, 255, 255, 0.2);
background: rgba(255, 255, 255, 0.1);
color: #ffffff;
font-size: 0.75rem;
cursor: pointer;
transition: all 0.3s ease;
}

.preview-btn:hover {
background: rgba(0, 242, 254, 0.7);
border-color: #00f2fe;
color: #000000;
}

.edit-btn:hover {
background: rgba(255, 255, 255, 0.25);
border-color: rgba(255, 255, 255, 0.4);
}
</style>
