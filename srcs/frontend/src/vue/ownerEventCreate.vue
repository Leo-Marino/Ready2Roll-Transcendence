<template>
  <div class="owner-visual-wrapper">
    <!-- Sfondo Video -->
    <video autoplay muted loop playsinline id="bgVideo">
      <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4" />
    </video>

    <!-- Input file nascosto per upload media -->
    <input 
      type="file" 
      ref="fileInput" 
      accept="image/png, image/jpeg, video/mp4" 
      style="display: none;" 
      @change="handleFileUpload" 
    />

    <!-- HEADER -->
    <header class="app-header">
      <div class="logo">Ready2Roll</div>
      <div class="user-profile">
        <span>Alek (OWNER)</span>
        <span class="avatar">👤</span>
      </div>
    </header>

    <main class="main-content">
      <!-- HEADER PAGINA E PULSANTE NAVIGAZIONE MOSTRA EVENTI -->
      <div v-if="!isExpanded" class="page-title-row">
        <h1 class="page-title">CREA UN NUOVO EVENTO</h1>
        <button class="action-btn nav-visual-btn" @click="goToVisualPage">
          📂 I MIEI EVENTI
        </button>
      </div>

      <!-- MAIN CARD SIMULATORE & FORM -->
      <section class="glass-card" :class="{ 'is-expanded-card': isExpanded }">
        
        <!-- PANNELLO DETTAGLI EVENTO (Titolo, Data Calendario, Stato) -->
        <div v-if="!isExpanded" class="event-details-bar">
          <div class="detail-input-group flex-2">
            <label for="event-title">TITOLO EVENTO *</label>
            <input 
              id="event-title"
              type="text" 
              v-model="eventTitle" 
              placeholder="Es. YAB Night Club Party" 
              class="custom-input"
            />
          </div>
          
          <!-- SELEZIONE DATA DA CALENDARIO -->
          <div class="detail-input-group flex-1">
            <label for="event-date">DATA EVENTO *</label>
            <input 
              id="event-date"
              type="date" 
              v-model="eventDate" 
              class="custom-input date-picker"
            />
          </div>

          <div class="detail-input-group flex-1">
            <label for="event-status">STATO</label>
            <select id="event-status" v-model="eventStatus" class="custom-input custom-select">
              <option value="Attivo">Attivo</option>
              <option value="Bozza">Bozza</option>
              <option value="Programmato">Programmato</option>
            </select>
          </div>
        </div>

        <!-- SIMULATORE VISUALIZZAZIONE & MAPPA -->
        <div class="preview-box" :class="{ 'is-expanded-box': isExpanded, 'is-map-view': isMapOpen && !isExpanded }">
        
          <!-- Sidebar Sinistra (Menu) - visibile solo espanso -->
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

          <!-- Content-Dedicated Container (Simulatore Mobile) -->
          <div class="media-outer-wrapper" :class="{ 'is-expanded-wrapper': isExpanded }">
            <div 
              class="media-preview clickable" 
              :class="{ 'has-content': uploadedMediaSrc, 'is-expanded': isExpanded }"
              @mouseenter="hoverStep = 1"
              @mouseleave="hoverStep = null"
              @click="handleMediaClick"
            >
              <!-- Icona mappa: toggle apertura mappa -->
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

              <!-- Tasto Espandi / Comprimi Fullscreen -->
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

              <template v-if="!uploadedMediaSrc">
                <span>Clicca per inserire Foto/Video</span>
              </template>
              <template v-else>
                <video 
                  v-if="mediaType === 'video'" 
                  :src="uploadedMediaSrc" 
                  autoplay 
                  loop 
                  muted 
                  class="uploaded-preview"
                ></video>
                <img 
                  v-else 
                  :src="uploadedMediaSrc" 
                  alt="Anteprima" 
                  class="uploaded-preview" 
                />
              </template>

              <!-- Descrizione Evento (Overlay Editable) -->
              <div 
                class="text-preview overlay-description"
                @mouseenter="hoverStep = 3"
                @mouseleave="hoverStep = null"
                @click.stop="selectStep(3)"
              >
                <textarea 
                  v-model="descriptionText" 
                  placeholder="Inserisci descrizione / hashtag..."
                  class="editable-description"
                  rows="2"
                  @focus="selectStep(3)"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- SEZIONE MAPPA (Visibile solo in modalità compatta e se isMapOpen è true) -->
          <div v-if="isMapOpen && !isExpanded" class="map-container">
            <div class="map-inner-wrapper">
              <div class="map-search-bar">
                <input 
                  type="text" 
                  placeholder="Cerca indirizzo locale..." 
                  class="custom-input map-input" 
                  v-model="eventLocation" 
                />
                <button class="action-btn-small">Cerca</button>
              </div>
              <iframe 
                width="100%" 
                height="100%" 
                frameborder="0" 
                scrolling="no" 
                marginheight="0" 
                marginwidth="0" 
                :src="`https://maps.google.com/maps?q=${encodeURIComponent(eventLocation)}&t=&z=15&ie=UTF8&iwloc=&output=embed`"
                class="map-iframe"
              ></iframe>
            </div>
          </div>

          <!-- Sidebar Destra (Info Owner + Commenti) - visibile solo espanso -->
          <aside v-if="isExpanded" class="sidebar-right">
            <div class="side-card owner-info-box">
              <div class="owner-header">
                <div>
                  <strong>local owner ✓</strong><br>
                  <small>@club1 · 2h ago</small>
                </div>
                <button class="sub-btn">Subscribe</button>
              </div>
              <p class="post-caption">{{ descriptionText || 'Nessuna descrizione.' }}</p>
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

        <!-- AZIONE PRINCIPALE: TASTO PUBBLICA -->
        <div v-if="!isExpanded" class="publish-action-bar">
          <button class="publish-btn" @click="handlePublish">
            PUBBLICA EVENTO
          </button>
        </div>

      </section>
    </main>
  </div>
</template>

<script>
export default {
  name: 'CreateEvent',
  emits: ['navigate-view', 'event-published'],
  data() {
    return {
      activeStep: 1,
      hoverStep: null,
      eventTitle: '',
      eventDate: '', // Salva il valore formattato YYYY-MM-DD dal calendario
      eventStatus: 'Attivo',
      descriptionText: '',
      uploadedMediaSrc: null,
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
    handlePublish() {
      const newEventData = {
        title: this.eventTitle || 'Nuovo Evento',
        location: this.eventLocation,
        date: this.formattedDate,
        rawDate: this.eventDate,
        status: this.eventStatus,
        description: this.descriptionText,
        mediaSrc: this.uploadedMediaSrc,
        mediaType: this.mediaType || 'image'
      };

      this.$emit('event-published', newEventData);
      this.goToVisualPage();
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

<style scoped>
:root {
  --font-bruno: 'Bruno Ace', cursive, sans-serif;
}

html, body, #app {
  margin: 0;
  padding: 0;
  font-family: var(--font-bruno);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.owner-visual-wrapper {
  position: relative;
  min-height: 100vh;
  width: 100%;
  color: #ffffff;
  font-family: "Bruno Ace", sans-serif;
  box-sizing: border-box;
  padding-bottom: 50px;
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

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.logo {
  font-weight: bold;
  font-size: 1.2rem;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  padding: 4px 8px;
}

.main-content {
  max-width: 98vw;
  margin: 0 auto;
  padding: 10px 20px;
  box-sizing: border-box;
}

.page-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1000px;
  margin: 0 auto 20px auto;
  flex-wrap: wrap;
  gap: 15px;
}

.page-title {
  margin: 0;
  font-size: 1.8rem;
}

.nav-visual-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  padding: 10px 20px;
  border-radius: 14px;
  font-family: "Bruno Ace", sans-serif;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-visual-btn:hover {
  background: rgba(0, 242, 254, 0.2);
  border-color: #00f2fe;
  color: #00f2fe;
}

.glass-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  box-sizing: border-box;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.5s ease;
  max-width: 1100px;
  margin: 0 auto;
}

.glass-card.is-expanded-card {
  background: transparent !important;
  border: none !important;
  backdrop-filter: none !important;
  padding: 0 !important;
  max-width: 100% !important;
}

/* Pannello Input Dettagli Evento */
.event-details-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  background: rgba(0, 0, 0, 0.25);
  padding: 15px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  flex-wrap: wrap;
}

.detail-input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: left;
}

.detail-input-group label {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.75);
}

.flex-1 { flex: 1; min-width: 160px; }
.flex-2 { flex: 2; min-width: 220px; }

.custom-input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.3);
  color: #FFFFFF;
  font-family: "Bruno Ace", sans-serif;
  font-size: 0.85rem;
  color-scheme: dark; /* Fa in modo che l'icona del calendario sia visibile bianca */
}

.date-picker {
  cursor: pointer;
}

.custom-input:focus {
  outline: none;
  border-color: #00f2fe;
}

.custom-select option {
  background: #111111;
  color: #ffffff;
}

/* Simulatore e Box Mappa */
.preview-box {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px;
  position: relative;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: stretch;
  gap: 20px;
  transition: all 0.5s ease;
}

.preview-box.is-map-view {
  justify-content: flex-start;
  padding: 20px;
}

.preview-box.is-expanded-box {
  width: 100% !important;
  max-width: 100% !important;
  justify-content: space-between !important;
  padding: 0 20px !important;
  margin: 0 !important;
  box-sizing: border-box;
  background: transparent !important;
  border: none !important;
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
  max-width: 360px;
  flex-shrink: 0;
  transition: all 0.5s ease;
}

.media-outer-wrapper.is-expanded-wrapper {
  max-width: 480px;
  height: calc(100vh - 90px);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 22px;
  padding: 10px;
  backdrop-filter: blur(16px);
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
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.media-preview.is-expanded {
  border: 2px dashed rgba(255, 255, 255, 0.45) !important;
  height: 100%;
  width: 100%;
  border-radius: 16px;
}

.media-preview.clickable {
  cursor: pointer;
}

.media-preview.clickable:hover {
  border-color: rgba(0, 242, 254, 0.8);
}

.map-badge {
  position: absolute;
  top: 15px;
  left: 15px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 6px 10px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: all 0.3s ease;
}

.map-badge.clickable {
  cursor: pointer;
}

.map-badge.clickable:hover, .map-badge.active {
  background: rgba(0, 242, 254, 0.6);
  border-color: #ffffff;
}

.expand-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 10;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: #ffffff;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: background 0.3s ease;
}

.expand-btn:hover {
  background: rgba(0, 242, 254, 0.6);
}

.uploaded-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  opacity: 1;
  transition: opacity 0.3s ease;
}

.media-preview:not(.is-expanded) .uploaded-preview {
  opacity: 0.85;
}

.text-preview.overlay-description {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  z-index: 5;
  box-sizing: border-box;
  padding: 15px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.85), transparent);
}

.editable-description {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  color: #ffffff;
  font-family: "Bruno Ace", sans-serif;
  text-align: center;
  resize: none;
  font-size: 0.85rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
}

.editable-description::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

/* Sezione Mappa */
.map-container {
  flex-grow: 1;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 12px;
  backdrop-filter: blur(12px);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  animation: slideInMap 0.5s ease forwards;
}

.map-inner-wrapper {
  border: 2px dashed rgba(255, 255, 255, 0.5);
  border-radius: 18px;
  width: 100%;
  height: 100%;
  min-height: 380px;
  background: rgba(255, 255, 255, 0.03);
  position: relative;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.map-search-bar {
  display: flex;
  gap: 10px;
  padding: 12px;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(5px);
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.map-input {
  flex-grow: 1;
}

.map-iframe {
  flex-grow: 1;
  width: 100%;
  height: 100%;
  border-radius: 0 0 16px 16px;
  filter: invert(90%) hue-rotate(180deg) contrast(80%);
}

@keyframes slideInMap {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Sidebars Espanse */
.sidebar-left {
  width: 280px;
  flex-shrink: 0;
  height: calc(100vh - 90px);
}

.sidebar-right {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100vh - 90px);
}

.side-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 18px 20px;
  font-size: 0.85rem;
  text-align: left;
}

.side-card h4 {
  margin: 0 0 10px 0;
  font-size: 0.95rem;
}

.nav-menu, .sub-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-menu li, .sub-list li {
  padding: 6px 0;
  cursor: pointer;
  opacity: 0.85;
}

.owner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.sub-btn {
  background: #00f2fe;
  border: none;
  color: #000;
  font-weight: bold;
  padding: 4px 10px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.75rem;
}

.post-caption {
  font-size: 0.8rem;
  opacity: 0.9;
  margin: 0;
  line-height: 1.3;
}

.comment-item {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px 0;
}

.comment-item:last-child {
  border-bottom: none;
}

.action-btn-small {
  background: rgba(0, 242, 254, 0.6);
  border: 1px solid rgba(0, 242, 254, 0.8);
  color: #ffffff;
  padding: 6px 16px;
  border-radius: 12px;
  cursor: pointer;
  font-family: "Bruno Ace", sans-serif;
  font-size: 0.8rem;
  transition: all 0.3s ease;
}

.action-btn-small:hover {
  background: rgba(0, 242, 254, 0.8);
}

/* Tasto Pubblica Evento */
.publish-action-bar {
  margin-top: 25px;
  display: flex;
  justify-content: center;
}

.publish-btn {
  background: rgba(0, 242, 254, 0.2);
  border: 1px solid #00f2fe;
  color: #00f2fe;
  padding: 14px 40px;
  font-size: 0.95rem;
  font-weight: bold;
  font-family: "Bruno Ace", sans-serif;
  border-radius: 14px;
  cursor: pointer;
  box-shadow: 0 0 15px rgba(0, 242, 254, 0.3);
  transition: all 0.3s ease;
}

.publish-btn:hover {
  background: #00f2fe;
  color: #000000;
  box-shadow: 0 0 25px rgba(0, 242, 254, 0.8);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .preview-box.is-map-view {
    flex-direction: column;
  }
  .media-outer-wrapper {
    max-width: 100%;
  }
  .event-details-bar {
    flex-direction: column;
  }
  .page-title-row {
    flex-direction: column;
  }
}
</style>