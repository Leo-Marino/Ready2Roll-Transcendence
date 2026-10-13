<script>
export default {
  name: 'CreateEvent',
  emits: ['navigate-view', 'event-published'],
  data() {
    return {
      activeStep: 1,
      hoverStep: null,
      eventTitle: '',
      eventDate: '',
      eventStatus: 'Attivo',
      descriptionText: '',
      uploadedMediaSrc: null,
      actualFile: null,
      mediaType: null,
      isExpanded: false,
      isMapOpen: false,
      eventLocation: 'YAB, Firenze'
    }
  },
  computed: {
    currentStep() {
      return this.hoverStep !== null ? this.hoverStep : this.activeStep;
    },
    formattedDate() {
      if (!this.eventDate) return 'Data da definire';
      const [year, month, day] = this.eventDate.split('-');
      return `${day}/${month}/${year}`;
    }
  },
  methods: {
    goToCreateEvent() {
      this.$router.push('/CreateEvent');
    },
    selectStep(stepNumber) {
      this.activeStep = stepNumber;
    },
    handleMediaClick() {
      if (!this.uploadedMediaSrc) {
        this.selectStep(1);
        this.triggerFileInput();
      }
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.uploadedMediaSrc = URL.createObjectURL(file);
        this.actualFile = file;
        this.mediaType = file.type.startsWith('video') ? 'video' : 'image';
      }
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
    async handlePublish() {
      const token = localStorage.getItem('token') || localStorage.getItem('access');

      const formData = new FormData();
      formData.append('title', this.eventTitle || 'Nuovo Evento');
      formData.append('location', this.eventLocation);
      formData.append('event_date', this.eventDate);
      formData.append('status', this.eventStatus);
      formData.append('description', this.descriptionText);
      formData.append('media_type', this.mediaType || 'image');

      if (this.actualFile) {
        formData.append('media_file', this.actualFile);
      }

      try {
        const response = await fetch('/api/events/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });

        if (response.ok) {
          const createdEvent = await response.json();
          alert("Event created successfully!!");
          this.$emit('event-published', createdEvent);
          this.goToVisualPage();
        } else {
          const errorData = await response.json();
          console.error("Backend error:", errorData);
          alert("There was an error loading the event");
        }
      } catch (error) {
        console.error("Network error,", error);
        alert("Unable to connect to the backend server");
      }
    },

    goToVisualPage() {
      if (this.$router) {
        this.$router.push('/ViewEvent');
      }
      this.$emit('navigate-view');
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

    <div v-if="activePreviewEvent" class="fullscreen-preview-overlay">
      <button class="fullscreen-close-btn" @click="closePreview">✕</button>

      <div class="fullscreen-content-container">
        <section class="glass-card" :class="{ 'is-expanded-card': isExpanded }">
          <div 
            class="preview-box" 
            :class="{ 
              'is-expanded-box': isExpanded, 
              'is-map-view': isMapOpen && !isExpanded 
            }"
          >
            <aside v-if="isExpanded" class="sidebar-left">
              <div class="side-card">
                <h4>Menu</h4>
                <ul class="nav-menu">
                  <li>🔥 For you</li>
                  <li>📱 Subscription</li>
                  <li>🧩 Discover</li>
                </ul>
                <h4 style="margin-top: 20px;">Subscribed accounts</h4>
                <ul class="sub-list">
                  <li>👤 Xhul</li>
                  <li>👤 Anna</li>
                  <li>👤 thilina</li>
                </ul>
                <small class="show-more">show more _</small>
              </div>
            </aside>

            <div class="media-outer-wrapper" :class="{ 'is-expanded-wrapper': isExpanded }">
              <div 
                class="media-preview" 
                :class="{ 'has-content': activePreviewEvent.media_src, 'is-expanded': isExpanded }"
              >
                <div 
                  v-if="!isExpanded"
                  class="map-badge clickable"
                  :class="{ active: isMapOpen }"
                  @click.stop="toggleMap"
                >
                  <svg class="maps-icon" viewBox="0 0 24 24" width="20" height="20">
                    <path fill="#EA4335" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                    <circle fill="#FFFFFF" cx="12" cy="9" r="2.5"/>
                  </svg>
                </div>
                <button 
                  class="expand-btn" 
                  @click.stop="toggleExpand" 
                  title="Ingrandisci"
                >
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <path v-if="!isExpanded" d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
                    <path v-else d="M4 14h6v6M20 10h-6V4M10 14L3 21M14 10l7-7"/>
                  </svg>
                </button>
                <video 
                  v-if="activePreviewEvent.media_type === 'video'" 
                  :src="activePreviewEvent.media_src" 
                  autoplay 
                  loop 
                  muted 
                  class="uploaded-preview"
                ></video>
                <img 
                  v-else 
                  :src="activePreviewEvent.media_src" 
                  alt="Preview" 
                  class="uploaded-preview" 
                />
                <div class="text-preview overlay-description">
                  <p class="preview-description-text">
                    {{ activePreviewEvent.description }}
                  </p>
                </div>
              </div>
            </div>

            <div v-if="isMapOpen && !isExpanded" class="map-container">
              <div class="map-inner-wrapper">
                <div class="map-search-bar">
                  <input 
                    type="text" 
                    v-model="activePreviewEvent.location" 
                    class="custom-input map-input" 
                    readonly 
                  />
                </div>
                <iframe 
                  width="100%" 
                  height="100%" 
                  frameborder="0" 
                  scrolling="no" 
                  marginheight="0" 
                  marginwidth="0" 
                  :src="`https://maps.google.com/maps?q=${encodeURIComponent(activePreviewEvent.location)}&t=&z=15&ie=UTF8&iwloc=&output=embed`"
                  class="map-iframe"
                ></iframe>
              </div>
            </div>

            <aside v-if="isExpanded" class="sidebar-right">
              <div class="side-card owner-info-box">
                <div class="owner-header">
                  <div>
                    <strong>local owner ✓</strong><br>
                    <small>@club1 · 2h ago</small>
                  </div>
                  <button class="sub-btn">Subscribe</button>
                </div>
                <p class="post-caption">{{ activePreviewEvent.description }}</p>
              </div>

              <div class="side-card comments-box">
                <h4>Comments</h4>
                <div class="comment-item">
                  <strong>Xhul</strong>
                  <p>The drop on that first track was insanity!</p>
                </div>
                <div class="comment-item">
                  <strong>Anna</strong>
                  <p>Best set of the year so far!</p>
                </div>
              </div>
            </aside>
          </div>
        </section>
      </div>
    </div>

    <div v-if="isEditing" class="edit-modal-overlay" @click.self="closeEdit">
      <div class="edit-modal-card glass-card">
        <div class="edit-modal-header">
          <h2>MODIFICA EVENTO</h2>
          <button class="icon-close-btn" @click="closeEdit">✕</button>
        </div>

        <form @submit.prevent="saveEdit" class="edit-form">
          <div class="form-group">
            <label>Titolo Evento</label>
            <input type="text" v-model="editForm.title" class="custom-input" required />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Luogo / Location</label>
              <input type="text" v-model="editForm.location" class="custom-input" required />
            </div>
            <div class="form-group">
              <label>Data Evento</label>
              <input type="date" v-model="editForm.event_date" class="custom-input" required />
            </div>
          </div>

          <div class="form-group">
            <label>Stato Evento</label>
            <select v-model="editForm.status" class="custom-input custom-select">
              <option value="Attivo">Attivo</option>
              <option value="Bozza">Bozza</option>
              <option value="Programmato">Programmato</option>
            </select>
          </div>

          <div class="form-group">
            <label>Descrizione</label>
            <textarea v-model="editForm.description" rows="3" class="custom-input textarea-input"></textarea>
          </div>

          <div class="form-group">
            <label>Media (Foto/Video)</label>
            <div class="media-edit-preview-box">
              <img v-if="editForm.media_type === 'image'" :src="editForm.media_src" class="edit-thumb-preview" />
              <video v-else :src="editForm.media_src" class="edit-thumb-preview" autoplay muted loop></video>

              <input 
                type="file" 
                ref="editFileInput" 
                accept="image/png, image/jpeg, video/mp4" 
                style="display: none;" 
                @change="handleEditFileUpload" 
              />
              <button type="button" class="action-btn upload-change-btn" @click="triggerEditFileInput">
                📷 Cambia Foto/Video
              </button>
            </div>
          </div>

          <div class="edit-modal-actions">
            <button type="button" class="action-btn cancel-btn" @click="closeEdit">Annulla</button>
            <button type="submit" class="action-btn save-btn">💾 Salva Modifiche</button>
          </div>
        </form>
      </div>
    </div>
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

.create-nav-btn:hover .btn-icon {
  background: rgba(10, 10, 15, 0.2);
  transform: rotate(90deg);
}

.create-nav-btn .btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 242, 254, 0.25);
  border-radius: 50%;
  padding: 4px;
  transition: transform 0.4s ease, background 0.3s ease;
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

.fullscreen-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(10, 10, 15, 0.95);
  backdrop-filter: blur(16px);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  padding: 20px;
  overflow: hidden;
}

.fullscreen-close-btn {
  position: absolute;
  top: 20px;
  right: 25px;
  z-index: 2010;
  background: rgba(255, 71, 87, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: #ffffff;
  padding: 10px 20px;
  border-radius: 30px;
  cursor: pointer;
  font-size: 0.85rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
}

.fullscreen-close-btn:hover {
  background: #ff4757;
  transform: scale(1.05);
}

.fullscreen-content-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-box {
  background: rgba(0, 0, 0, 0.45);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px;
  position: relative;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: stretch;
  gap: 20px;
  transition: all 0.5s ease;
  max-height: 90vh;
}

.media-outer-wrapper {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 12px;
  backdrop-filter: blur(12px);
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  max-width: 380px;
  height: calc(85vh);
  flex-shrink: 0;
  transition: all 0.5s ease;
}

.media-preview {
  border: 2px dashed rgba(255, 255, 255, 0.5);	
  border-radius: 18px;
  width: 100%;
  aspect-ratio: 9 / 16;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
  position: relative;
  box-sizing: border-box;
}

.uploaded-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.custom-input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.3);
  color: #FFFFFF;
  font-size: 0.85rem;
  color-scheme: dark;
}

@media (max-width: 768px) {
  .events-grid {
    grid-template-columns: 1fr;
  }
}
</style>
