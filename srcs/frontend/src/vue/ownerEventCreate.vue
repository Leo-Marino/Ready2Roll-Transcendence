<template>
<div class="owner-visual-wrapper">
    <video autoplay muted loop playsinline id="bgVideo">
    <source src="../assets/ready2roll_wave_background.mp4" type="video/mp4">
    </video>
    <input 
    type="file" 
    ref="fileInput" 
    accept="image/png, video/mp4" 
    style="display: none;" 
    @change="handleFileUpload" 
    />
    <!-- PRIMA PAGINA - CREAZINE DI UN EVENTO NUOVO-->
    <header class="app-header">
    <div class="logo">Ready2Roll</div>
    <div class="user-profile">
        <span>Alek (OWNER)</span>
        <span class="avatar">👤</span>
    </div>
    </header>

    <main class="main-content">
    <h1 v-if="!isExpanded" class="page-title">CREA UN NUOVO EVENTO</h1>

    <!-- step navigation 1 / 2 / 3 / 4 -->
    <nav v-if="!isExpanded" class="stepper">
        <button 
          class="step-btn" 
          :class="{ active: currentStep === 1 }" 
          @click="currentStep = 1"
        >
          1. Scenery
        </button>
        <button 
          class="step-btn" 
          :class="{ active: currentStep === 2 }" 
          @click="currentStep = 2"
        >
          2. Location
        </button>
        <button 
          class="step-btn" 
          :class="{ active: currentStep === 3 }" 
          @click="currentStep = 3"
        >
          3. Riepilogo
        </button>
        <button 
          class="step-btn" 
          :class="{ active: currentStep === 4 }" 
          @click="currentStep = 4"
        >
          4. Pubblica
        </button>
    </nav>

    <!-- simulatore visualizzazione -->
    <section class="glass-card" :class="{ 'is-expanded-card': isExpanded }">
        <h3 v-if="!isExpanded">* Simulatore visualizzazione *</h3>

        <div class="preview-box" :class="{ 'is-expanded-box': isExpanded }">
        <!-- Sidebar Sinistra (Menu) -->
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

        <!-- Contenitore centrale (Box trasparente esterno) -->
        <div class="media-outer-wrapper" :class="{ 'is-expanded-wrapper': isExpanded }">
            <!-- 2 - background photos/videos area (Box interna tratteggiata) -->
            <div 
              class="media-preview clickable" 
              :class="{ 'has-content': uploadedMediaSrc, 'is-expanded': isExpanded }"
              @mouseenter="hoverStep = 1"
              @mouseleave="hoverStep = null"
              @click="handleMediaClick"
            >
                <!-- 1 - icona google maps -->
                <div 
                  v-if="!isExpanded"
                  class="map-badge clickable"
                  @click.stop="selectStep(2)"
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

                <template v-if="!uploadedMediaSrc">
                <span>Scegli foto/video</span>
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

                <!-- 3 - descrizione evento -->
                <div 
                  class="text-preview overlay-description"
                  @mouseenter="hoverStep = 3"
                  @mouseleave="hoverStep = null"
                  @click.stop="selectStep(3)"
                >
                    <textarea 
                    v-model="descriptionText" 
                    placeholder="Inserisci descrizione"
                    class="editable-description"
                    rows="2"
                    @focus="selectStep(3)"
                    ></textarea>
                </div>
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
            <p class="post-caption">Florence was on fire last night! Incredible sets... #nightlife #party</p>
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
    </main>

    <div class="section-divider"></div>

<!-- PRIMA PAGINA - VISUALIZZAZIONE DI UN EVENTO-->
    <header class="app-header">
    <div class="logo">Ready2Roll</div>
    <div class="user-profile">
        <span>Alek (<span style="color: #00f2fe;">OWNER</span>)</span>
        <span class="avatar">👤</span>
    </div>
    </header>

    <main class="main-content">
    <div class="event-title-container">
        <h2>VISUALIZZA *nome evento*</h2>
        <span class="status-badge">ATTIVO</span>
        <span class="info-badge">i</span>
    </div>
    <div class="grid-container">
        <div class="column">
        <div class="row">
            <!-- panoramica -->
            <div class="glass-card card-flex">
            <h4>PANORAMICA</h4>
            <div class="stats-box">
                <div>
                <div class="stat-number">6</div>
                <small>PARTECIPANTI</small>
                </div>
                <div class="stat-divider">
                <div class="stat-number">7</div>
                <small>NON SICURI</small>
                </div>
            </div>
            <div style="margin-top: 15px;">
                <button class="action-btn">ALTRI DETTAGLI</button>
            </div>
            </div>

            <!-- posizione -->
            <div class="glass-card card-flex">
            <div class="card-header-flex">
                <h4>POSIZIONE</h4>
                <svg class="maps-icon" viewBox="0 0 24 24" width="20" height="20">
                <path fill="#EA4335" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                <circle fill="#FFFFFF" cx="12" cy="9" r="2.5"/>
                </svg>
            </div>
            <div class="map-placeholder">
                <span>[ MAPPA ]</span>
            </div>
            </div>
        </div>

        <!-- lista iscritti -->
        <div class="glass-card">
            <div class="card-header-flex" style="margin-bottom: 15px;">
            <h4>LISTA ISCRITTI</h4>
            <button class="action-btn-small">Filtra</button>
            </div>
            
            <div class="input-container">
            <input type="text" placeholder="Cerca..." class="custom-input" />
            </div>

            <ul class="user-list">
            <li>
                <div><span>👤</span> Alex Degli Innocenti</div>
                <span>&gt;</span>
            </li>
            <li>
                <div><span>👤</span> Ilyas Mahjoubi</div>
                <span>&gt;</span>
            </li>
            </ul>
        </div>
        </div>
        <div class="column">
        <!-- preview -->
        <div class="glass-card">
            <h4>PREVIEW</h4>
            <div class="inner-preview-box">
            <div class="preview-top-bar">
                <span class="mini-badge">
                <svg class="maps-icon" viewBox="0 0 24 24" width="14" height="14">
                    <path fill="#EA4335" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                    <circle fill="#FFFFFF" cx="12" cy="9" r="2.5"/>
                </svg>
                </span>
                <span class="dot-indicator"></span>
            </div>
            <div class="image-placeholder">
                [ IMMAGINE ]
            </div>
            </div>
            <div class="preview-details">
            <strong>FESTA A CASA DI ALEK!</strong>
            <div>📍 CASA MIA</div>
            <div>📅 27/07</div>
            </div>
        </div>

        <!-- crea comunicazione -->
        <div class="glass-card">
            <h4>CREA COMUNICAZIONE</h4>
            <div class="input-container" style="margin-top: 15px;">
            <textarea placeholder="Scrivi qualcosa..." class="custom-textarea"></textarea>
            </div>
            <div style="text-align: right; margin-top: 15px;">
            <button class="action-btn">Invia</button>
            </div>
        </div>
        </div>
    </div>
    </main>
</div>
</template>

<script>
export default {
name: 'CreateEvent',
data() {
    return {
    activeStep: 1,
    hoverStep: null,
    descriptionText: '',
    uploadedMediaSrc: null,
    mediaType: null,
    isExpanded: false
    }
},
computed: {
    currentStep() {
    return this.hoverStep !== null ? this.hoverStep : this.activeStep;
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
    }
}
}
</script>

<style scoped>
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

.page-title {
  text-align: center;
  margin-bottom: 25px;
  font-size: 1.8rem;
}

.stepper {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.step-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #FFFFFF;
  padding: 10px 18px;
  border-radius: 17px;
  cursor: pointer;
  font-family: "Bruno Ace", sans-serif;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.step-btn:hover, .step-btn.active {
  background: rgba(0, 242, 254, 0.67);
  border-color: transparent;
  color: #FFFFFF;
}

.glass-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  box-sizing: border-box;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.glass-card.is-expanded-card {
  background: transparent !important;
  border: none !important;
  backdrop-filter: none !important;
  padding: 0 !important;
}

.card-flex {
  flex: 1;
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-box {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px;
  margin: 20px auto;
  position: relative;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 20px;
}

.preview-box.is-expanded-box {
  width: 100% !important;
  max-width: 100% !important;
  justify-content: space-between !important;
  align-items: stretch !important;
  padding: 0 20px !important;
  margin: 0 !important;
  box-sizing: border-box;
  background: transparent !important;
  border: none !important;
}

/* Outer Wrapper trasparente in Fullscreen */
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
  transition: all 0.3s ease;
}

.media-outer-wrapper.is-expanded-wrapper {
  max-width: 480px;
  height: calc(100vh - 90px);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 22px;
  padding: 10px;
  backdrop-filter: blur(16px);
  box-sizing: border-box;
}

/* Inner Box tratteggiata per il contenuto */
.media-preview {
  border: 2px dashed rgba(255, 255, 255, 0.5);
  border-radius: 18px;
  width: 100%;
  aspect-ratio: 9 / 16;
  height: 100%;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
  scrollbar-width: none;
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

.media-preview::-webkit-scrollbar {
  display: none;
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

.map-badge.clickable:hover {
  background: rgba(0, 242, 254, 0.4);
  border-color: rgba(0, 242, 254, 0.8);
}

.maps-icon {
  display: block;
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

/* Regole per Opacità Immagine/Video */
.uploaded-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  opacity: 1; /* Default a 100% in fullscreen */
  transition: opacity 0.3s ease;
}

/* Semi-trasparente SOLO quando non è in fullscreen */
.media-preview:not(.is-expanded) .uploaded-preview {
  opacity: 0.6;
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
  border-top: none;
  margin-top: 0;
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
  font-size: 0.95rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
}

.editable-description::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

/* Sidebars layout ancorate ai bordi laterali */
.sidebar-left {
    width: 280px; /* Aumentata da 260px */
    flex-shrink: 0;
    height: calc(100vh - 90px);
}

.sidebar-right {
    width: 320px; /* Ingrandita come nella seconda immagine */
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px; /* SEPARA le due box tra di loro */
  height: calc(100vh - 90px);
}

.sidebar-right .owner-info-box {
  flex: 0 0 auto;
}

.sidebar-right .comments-box {
  flex: 1; /* Riempie lo spazio restante verso il basso */
  overflow-y: auto;
}

.side-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 18px 20px;
  font-size: 0.85rem;
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

.nav-menu li:hover, .sub-list li:hover {
  opacity: 1;
  color: #00f2fe;
}

.show-more {
  display: block;
  margin-top: 10px;
  opacity: 0.6;
  cursor: pointer;
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

.comment-item p {
  margin: 2px 0 0 0;
  font-size: 0.75rem;
  opacity: 0.8;
}

.legend-list {
  text-align: left;
  margin: 20px auto 0 auto;
  list-style-type: none;
  padding: 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
}

.legend-list li {
  margin-bottom: 6px;
}

.section-divider {
  margin: 50px 0;
  border-top: 1px dashed rgba(255, 255, 255, 0.3);
}

.event-title-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.status-badge {
  background: rgba(0, 242, 254, 0.3);
  border: 1px solid rgba(0, 242, 254, 0.8);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.info-badge {
  border: 1px solid #ffffff;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
}

.grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .grid-container {
    grid-template-columns: 1fr;
  }
  .sidebar-left, .sidebar-right {
    display: none;
  }
}

.column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.row {
  display: flex;
  gap: 20px;
}

.stats-box {
  display: flex;
  justify-content: space-around;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 12px 0;
  margin-top: 10px;
  text-align: center;
}

.stat-number {
  font-size: 1.4rem;
  font-weight: bold;
}

.stat-divider {
  border-left: 1px solid rgba(255, 255, 255, 0.2);
  padding-left: 15px;
}

.map-placeholder {
  border: 1px dashed rgba(255, 255, 255, 0.3);
  height: 100px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 10px;
  background: rgba(0, 0, 0, 0.15);
}

.action-btn {
  background: rgba(0, 242, 254, 0.67);
  color: #FFFFFF;
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 17px;
  cursor: pointer;
  font-family: "Bruno Ace", sans-serif;
  font-weight: 900;
  transition: background 0.3s ease;
}

.action-btn:hover {
  background: rgba(5, 212, 202, 0.8);
}

.action-btn-small {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  padding: 4px 12px;
  border-radius: 12px;
  cursor: pointer;
  font-family: "Bruno Ace", sans-serif;
  font-size: 0.75rem;
}

.custom-input, .custom-textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: #FFFFFF;
  font-family: "Bruno Ace", sans-serif;
}

.custom-textarea {
  height: 80px;
  resize: vertical;
}

.custom-input::placeholder, .custom-textarea::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.user-list {
  list-style: none;
  padding: 0;
  margin: 10px 0 0 0;
}

.user-list li {
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  padding: 10px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.inner-preview-box {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 12px;
  margin: 10px 0;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.preview-top-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.mini-badge {
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
}

.dot-indicator {
  border: 1px solid #ffffff;
  border-radius: 50%;
  width: 12px;
  height: 12px;
  display: inline-block;
}

.image-placeholder {
  border: 1px dashed rgba(255, 255, 255, 0.3);
  height: 80px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-details {
  margin-top: 10px;
  line-height: 1.6;
}
</style>