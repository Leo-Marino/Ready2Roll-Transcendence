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
    <!-- PRIMA PAGINA - CREAZIONE DI UN EVENTO NUOVO-->
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

        <!-- Aggiunta classe is-map-view per cambiare layout -->
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

        <!-- Contenitore centrale (Video/Foto) -->
        <div class="media-outer-wrapper" :class="{ 'is-expanded-wrapper': isExpanded }">
            <div 
              class="media-preview clickable" 
              :class="{ 'has-content': uploadedMediaSrc, 'is-expanded': isExpanded }"
              @mouseenter="hoverStep = 1"
              @mouseleave="hoverStep = null"
              @click="handleMediaClick"
            >
                <!-- 1 - icona mappa: toggle apertura mappa -->
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

        <!-- SEZIONE MAPPA (Visibile solo in modalità compatta e se isMapOpen è true) -->
        <div v-if="isMapOpen && !isExpanded" class="map-container">
            <div class="map-inner-wrapper">
                <!-- Barra di ricerca indirizzo finta -->
                <div class="map-search-bar">
                    <input type="text" placeholder="Cerca indirizzo locale..." class="custom-input map-input" v-model="eventLocation" />
                    <button class="action-btn-small">Cerca</button>
                </div>
                <!-- Iframe temporaneo (OpenStreetMap) al posto di Google Maps per non usare API Key a pagamento subito -->
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

    <!-- ... SECONDA PAGINA OMESSA PER BREVITÀ, IL CODICE È IDENTICO A PRIMA ... -->
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
    isExpanded: false,
    isMapOpen: false, // Nuovo stato per l'apertura mappa
    eventLocation: 'YAB, Firenze' // Testo base per la mappa
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
    // Se ingrandisco, chiudo la mappa
    if (this.isExpanded) this.isMapOpen = false;
    },
    // Nuova funzione per gestire il toggle della mappa
    toggleMap() {
        this.isMapOpen = !this.isMapOpen;
        if (this.isMapOpen) {
            this.selectStep(2);
        } else {
            this.selectStep(1);
        }
    }
}
}
</script>

<style scoped>
/* (Tutto il CSS precedente fino a .preview-box...) */

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
  transition: all 0.5s ease;
}

.glass-card.is-expanded-card {
  background: transparent !important;
  border: none !important;
  backdrop-filter: none !important;
  padding: 0 !important;
}

/* Base della Preview Box: layout normale al centro */
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
  align-items: stretch; /* Stretch per farli alti uguali */
  gap: 20px;
  transition: all 0.5s ease;
}

/* Modificatore per quando la mappa è aperta (Non full screen) */
.preview-box.is-map-view {
    justify-content: flex-start; /* Mette il video a sinistra */
    padding: 20px;
}

/* Layout espanso */
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

/* Contenitore Video/Immagine */
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
  
  /* Dimensione di default centrale */
  width: 100%;
  max-width: 360px;
  
  /* Se la mappa è aperta e non siamo in fullscreen, prendiamo circa 1/3 (max 360px va benissimo come colonna fissa) */
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

/* --- NUOVI STILI PER LA MAPPA --- */
.map-container {
    flex-grow: 1; /* Prende tutto il resto dello spazio (i restanti 2/3) */
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
    min-height: 400px;
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
    padding: 15px;
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
    filter: invert(90%) hue-rotate(180deg) contrast(80%); /* Semplice trucco CSS per far sembrare scura google maps embed free */
}

@keyframes slideInMap {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
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

.map-badge.active {
    background: rgba(0, 242, 254, 0.6);
    border-color: #fff;
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

.sidebar-right .owner-info-box {
  flex: 0 0 auto;
}

.sidebar-right .comments-box {
  flex: 1;
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

.custom-input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: #FFFFFF;
  font-family: "Bruno Ace", sans-serif;
}

.custom-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

/* Regole layout responsive per la mappa */
@media (max-width: 768px) {
  .preview-box.is-map-view {
      flex-direction: column;
  }
  .media-outer-wrapper {
      max-width: 100%;
  }
}
</style>