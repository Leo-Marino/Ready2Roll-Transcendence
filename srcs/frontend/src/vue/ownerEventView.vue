<template>
  <div class="owner-visual-wrapper">
    <!-- Sfondo Video -->
    <video autoplay muted loop playsinline id="bgVideo">
      <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4" />
    </video>
    <header class="app-header">
      <div class="logo">Ready2Roll</div>
      <div class="user-profile">
        <span>Alek (OWNER)</span>
        <span class="avatar">👤</span>
      </div>
    </header>
    <main class="main-content">
      <div class="page-header">
        <div class="header-top-row">
          <h1 class="page-title">I MIEI EVENTI</h1>
          <!-- Tasto di navigazione verso la Creazione Eventi -->
          <button class="action-btn create-nav-btn" @click="goToCreateEvent">
            ➕ CREA NUOVO EVENTO
          </button>
        </div>
        <p class="subtitle">Gestisci, modifica e visualizza l'anteprima a schermo intero delle tue serate</p>
      </div>

      <!-- SEZIONE GRID EVENTI -->
      <section class="events-grid">
        <div 
          v-for="event in eventsList" 
          :key="event.id" 
          class="event-card glass-card"
        >
          <div class="card-media-header">
            <img 
              v-if="event.mediaType === 'image'" 
              :src="event.mediaSrc" 
              alt="Cover evento" 
              class="card-thumb" 
            />
            <video 
              v-else 
              :src="event.mediaSrc" 
              autoplay 
              muted 
              loop 
              class="card-thumb"
            ></video>
            <span class="status-badge" :class="event.status.toLowerCase()">
              {{ event.status }}
            </span>
          </div>

          <div class="card-body">
            <h3 class="event-title">{{ event.title }}</h3>
            <div class="event-info-row">
              <span>📍 {{ event.location }}</span>
              <span>📅 {{ event.date }}</span>
            </div>
            <p class="event-description-truncated">
              {{ event.description || 'Nessuna descrizione inserita.' }}
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

      <!-- MODALE ANTEPRIMA A SCHERMO INTERO (FULLSCREEN) -->
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

              <!-- Media Wrapper (Simulatore Mobile 9:16) -->
              <div class="media-outer-wrapper" :class="{ 'is-expanded-wrapper': isExpanded }">
                <div 
                  class="media-preview" 
                  :class="{ 'has-content': activePreviewEvent.mediaSrc, 'is-expanded': isExpanded }"
                >
                  <!-- Icona Mappa Toggle -->
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

                  <!-- Tasto Ingrandisci / Comprimi -->
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

                  <!-- Preview Media -->
                  <video 
                    v-if="activePreviewEvent.mediaType === 'video'" 
                    :src="activePreviewEvent.mediaSrc" 
                    autoplay 
                    loop 
                    muted 
                    class="uploaded-preview"
                  ></video>
                  <img 
                    v-else 
                    :src="activePreviewEvent.mediaSrc" 
                    alt="Anteprima" 
                    class="uploaded-preview" 
                  />

                  <!-- Overlay Descrizione -->
                  <div class="text-preview overlay-description">
                    <p class="preview-description-text">
                      {{ activePreviewEvent.description }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Sezione Mappa (OpenStreetMap) -->
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

              <!-- Sidebar Destra (Info Owner + Commenti) -->
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

      <!-- MODALE MODIFICA EVENTO -->
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
                <input type="date" v-model="editForm.date" class="custom-input" required />
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
                <img v-if="editForm.mediaType === 'image'" :src="editForm.mediaSrc" class="edit-thumb-preview" />
                <video v-else :src="editForm.mediaSrc" class="edit-thumb-preview" autoplay muted loop></video>
                
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
        date: '',
        status: 'Attivo',
        description: '',
        mediaType: 'image',
        mediaSrc: ''
      },
      eventsList: [
        {
          id: 1,
          title: 'YAB Night Club Party',
          location: 'YAB, Firenze',
          date: '28 Febbraio 2026',
          status: 'Attivo',
          description: 'Florence was on fire last night! Incredible sets... #nightlife #party',
          mediaType: 'image',
          mediaSrc: 'https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?q=80&w=1000&auto=format&fit=crop'
        },
        {
          id: 2,
          title: 'Techno Basement Session',
          location: 'Tenax, Firenze',
          date: '05 Marzo 2026',
          status: 'Bozza',
          description: 'Preparatevi per un viaggio nei ritmi underground più spinti della capitale toscana!',
          mediaType: 'image',
          mediaSrc: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=1000&auto=format&fit=crop'
        },
        {
          id: 3,
          title: 'Spring Open Air Festival',
          location: 'Parco delle Cascine, Firenze',
          date: '12 Aprile 2026',
          status: 'Programmato',
          description: 'Musica dal vivo, food truck e relax sotto il sole per l\'apertura della stagione.',
          mediaType: 'image',
          mediaSrc: 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?q=80&w=1000&auto=format&fit=crop'
        }
      ]
    }
  },
  methods: {
    // Navigazione alla Pagina Creazione Eventi
    goToCreateEvent() {
      if (this.$router) {
        this.$router.push('/CreateEvent');
      }
      this.$emit('navigate-create');
    },

    // Gestione Anteprima Fullscreen
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
    },

    // Gestione Modifica Evento
    openEdit(event) {
      this.editForm = { ...event };
      this.isEditing = true;
    },
    closeEdit() {
      this.isEditing = false;
    },
    saveEdit() {
      const index = this.eventsList.findIndex(e => e.id === this.editForm.id);
      if (index !== -1) {
        this.eventsList.splice(index, 1, { ...this.editForm });
      }
      this.closeEdit();
    },
    triggerEditFileInput() {
      this.$refs.editFileInput.click();
    },
    handleEditFileUpload(e) {
      const file = e.target.files[0];
      if (file) {
        this.editForm.mediaSrc = URL.createObjectURL(file);
        this.editForm.mediaType = file.type.startsWith('video') ? 'video' : 'image';
      }
    }
  }
}
</script>

<style scoped>
/* Contenitore Base */
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
  box-sizing: border-box;
}

.page-header {
  text-align: center;
  margin-bottom: 35px;
}

.header-top-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.page-title {
  font-size: 2.2rem;
  margin: 0;
  letter-spacing: 1px;
}

.create-nav-btn {
  flex: initial;
  background: rgba(0, 242, 254, 0.2);
  border: 1px solid #00f2fe;
  color: #00f2fe;
  padding: 10px 20px;
  font-weight: bold;
  font-size: 0.85rem;
  border-radius: 14px;
  box-shadow: 0 0 12px rgba(0, 242, 254, 0.3);
  transition: all 0.3s ease;
}

.create-nav-btn:hover {
  background: #00f2fe;
  color: #000000;
  box-shadow: 0 0 20px rgba(0, 242, 254, 0.7);
  transform: translateY(-2px);
}

.subtitle {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* LAYOUT GRID BOX EVENTI */
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
  font-family: "Bruno Ace", sans-serif;
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

/* ANTEPRIMA A SCHERMO INTERO (FULLSCREEN) */
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
  font-family: "Bruno Ace", sans-serif;
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

/* STILI SIMULATORE ESPANSO & COMPATTO */
.glass-card.is-expanded-card {
  background: transparent !important;
  border: none !important;
  backdrop-filter: none !important;
  padding: 0 !important;
  width: 100%;
  height: 100%;
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

.preview-box.is-map-view {
  justify-content: flex-start;
  width: 90vw;
  max-width: 1100px;
}

.preview-box.is-expanded-box {
  width: 100vw !important;
  height: 90vh !important;
  max-width: 100% !important;
  justify-content: space-between !important;
  padding: 0 !important;
  margin: 0 !important;
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
  max-width: 380px;
  height: calc(85vh);
  flex-shrink: 0;
  transition: all 0.5s ease;
}

.media-outer-wrapper.is-expanded-wrapper {
  max-width: 480px;
  height: 100%;
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
  box-sizing: border-box;
}

.media-preview.is-expanded {
  border: 2px dashed rgba(255, 255, 255, 0.45) !important;
  height: 100%;
  width: 100%;
  border-radius: 16px;
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
  cursor: pointer;
}

.map-badge:hover, .map-badge.active {
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

.preview-description-text {
  margin: 0;
  font-size: 0.85rem;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
}

/* MAPPA E SIDEBARS */
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
  padding: 12px;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(5px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.map-iframe {
  flex-grow: 1;
  width: 100%;
  height: 100%;
  border-radius: 0 0 16px 16px;
  filter: invert(90%) hue-rotate(180deg) contrast(80%);
}

.sidebar-left {
  width: 280px;
  flex-shrink: 0;
  height: 100%;
}

.sidebar-right {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: 100%;
}

.side-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 16px;
  font-size: 0.8rem;
  text-align: left;
}

.side-card h4 {
  margin: 0 0 10px 0;
}

.nav-menu, .sub-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-menu li, .sub-list li {
  padding: 5px 0;
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
  font-size: 0.7rem;
}

.post-caption {
  font-size: 0.78rem;
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

.comment-item p {
  margin: 2px 0 0 0;
  font-size: 0.75rem;
  opacity: 0.8;
}

/* MODALE MODIFICA EVENTO */
.edit-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  z-index: 1500;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
}

.edit-modal-card {
  width: 100%;
  max-width: 580px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid rgba(0, 242, 254, 0.4);
}

.edit-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  padding-bottom: 10px;
}

.edit-modal-header h2 {
  font-size: 1.3rem;
  margin: 0;
}

.icon-close-btn {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 1.2rem;
  cursor: pointer;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: left;
}

.form-group label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
}

.custom-input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.3);
  color: #ffffff;
  font-family: "Bruno Ace", sans-serif;
  font-size: 0.85rem;
}

.custom-input:focus {
  outline: none;
  border-color: #00f2fe;
}

.custom-select {
  cursor: pointer;
}

.custom-select option {
  background: #111;
  color: #fff;
}

.textarea-input {
  resize: vertical;
}

.media-edit-preview-box {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.05);
  padding: 10px;
  border-radius: 12px;
}

.edit-thumb-preview {
  width: 70px;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.upload-change-btn {
  font-size: 0.75rem;
}

.edit-modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 10px;
}

.save-btn {
  background: rgba(0, 242, 254, 0.8);
  border-color: #00f2fe;
  color: #000000;
  font-weight: bold;
}

.save-btn:hover {
  background: #00f2fe;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
}

.cancel-btn:hover {
  background: rgba(255, 71, 87, 0.6);
}

/* Responsive */
@media (max-width: 768px) {
  .events-grid {
    grid-template-columns: 1fr;
  }
  .header-top-row {
    flex-direction: column;
  }
  .form-row {
    flex-direction: column;
  }
  .preview-box.is-map-view {
    flex-direction: column;
  }
  .media-outer-wrapper {
    max-width: 100%;
  }
}
</style>