<script>
export default {
  name: 'CreateEvent',
  emits: ['navigate-view', 'event-published'],
  data() {
    return {
      activeStep: 1, // 1: Map (Left), 2: Media (Center), 3: Details Form (Right)
      eventTitle: '',
      descriptionText: '',
      eventLocation: 'YAB Club, Florence',
      eventDate: '',
      maxCapacity: '',
      ticketPrice: '',
      endTime: '',
      eventTags: '',
      eventStatus: 'Draft',
      uploadedMediaSrc: null,
      actualFile: null,
      mediaType: null
    }
  },
  computed: {
    formattedDate() {
      if (!this.eventDate) return 'Date TBD';
      const parts = this.eventDate.split('T')[0].split('-');
      if (parts.length === 3) {
        const [year, month, day] = parts;
        return `${day}/${month}/${year}`;
      }
      return this.eventDate;
    }
  },
  methods: {
    goToStep(stepNumber) {
      this.activeStep = stepNumber;
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
      event.target.value = '';
    },
    async handlePublish() {
      if (!this.eventTitle || !this.descriptionText || !this.eventDate || !this.eventStatus) {
        alert("All mandatory fields must be filled!");
        return;
      }

      const token = localStorage.getItem('token') || localStorage.getItem('access');

      const formData = new FormData();
      formData.append('title', this.eventTitle);
      formData.append('description', this.descriptionText);
      formData.append('location', this.eventLocation);
      formData.append('event_date', this.eventDate);
      formData.append('status', this.eventStatus);

      if (this.maxCapacity) formData.append('max_capacity', this.maxCapacity);
      if (this.ticketPrice) formData.append('ticket_price', this.ticketPrice);
      if (this.endTime) formData.append('end_time', this.endTime);
      if (this.eventTags) formData.append('tags', this.eventTags);

      if (this.actualFile) {
        formData.append('media_file', this.actualFile);
        formData.append('media_type', this.mediaType);
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
          alert("Event created successfully!");
          this.$emit('event-published', createdEvent);
          this.goToVisualPage();
        } else {
          const errorData = await response.json();
          console.error("Backend error:", errorData);
          alert("There was an error creating the event");
        }
      } catch (error) {
        console.error("Network error", error);
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
  <input
    type="file"
    ref="fileInput"
    accept="image/png, image/jpeg, video/mp4"
    style="display: none;"
    @change="handleFileUpload"
  />
  
  <header class="navbar glass-panel">
    <div class="nav-left">
      <div class="logo" @click="$router.push('/home')">
        <img src="../assets/logo_temp.png" alt="Ready2Roll Logo" class="nav-logo-img" />
        <span class="logo-text">Ready2Roll</span>
      </div>
    </div>

    <div class="nav-right">
      <div class="nav-icons">
        <router-link to="/direct" class="nav-icon-link" title="Direct Messages">
          <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
          </svg>
        </router-link>
        <router-link to="/chat" class="nav-icon-link" title="Chat">
          <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a.75.75 0 01-.81-.54 2.89 2.89 0 01.213-1.637 8.25 8.25 0 01-1.813-5.293C3 7.444 7.03 3.75 12 3.75s9 3.694 9 8.25z" />
          </svg>
        </router-link>
        <router-link to="/profile" class="nav-icon-link" title="Profile">
          <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
        </router-link>
      </div>
    </div>
  </header>

  <main class="main-content">
    <div class="page-title-row">
      <h1 class="page-title">CREATE AN EVENT</h1>
      <button class="action-btn nav-visual-btn" @click="goToVisualPage">
        📂 MY EVENTS
      </button>
    </div>

    <section class="glass-card">
      <div class="preview-box">
        
        <!-- STEP 1: MAP LOCATION (LEFT) -->
        <div class="step-column" :class="{ 'step-active': activeStep === 1 }" @click="goToStep(1)">
          <div class="step-header-label">1. MAP LOCATION</div>
          <div class="map-container-inline">
            <div class="map-inner-wrapper">
              <div class="map-search-bar">
                <input
                  type="text"
                  placeholder="Find desired address or location"
                  class="custom-input map-input"
                  v-model="eventLocation"
                />
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
        </div>

        <!-- STEP 2: CONTENT MEDIA (CENTER) -->
        <div class="step-column" :class="{ 'step-active': activeStep === 2 }" @click="goToStep(2)">
          <div class="step-header-label">2. CONTENT MEDIA</div>
          <div class="media-outer-wrapper">
            <div
              class="media-preview clickable"
              :class="{ 'has-content': uploadedMediaSrc }"
              @click="goToStep(2); triggerFileInput()"
            >
              <template v-if="!uploadedMediaSrc">
                <span>Click here to insert photo/video</span>
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
                  alt="Preview"
                  class="uploaded-preview"
                />
              </template>
            </div>
          </div>
        </div>

        <!-- STEP 3: EVENT DETAILS (RIGHT) -->
        <div class="step-column right-section" :class="{ 'step-active': activeStep === 3 }" @click="goToStep(3)">
          <div class="step-header-label">3. EVENT DETAILS</div>
          <div class="event-details-bar-vertical">
            
            <div class="detail-input-group">
              <label for="event-title">TITLE *</label>
              <input
                id="event-title"
                type="text"
                v-model="eventTitle"
                placeholder="E.g. Night Club Party"
                class="custom-input"
                required
              />
            </div>

            <div class="detail-input-group">
              <label for="event-description">DESCRIPTION *</label>
              <textarea
                id="event-description"
                v-model="descriptionText"
                placeholder="Describe your event..."
                class="custom-input textarea-input"
                rows="2"
                required
              ></textarea>
            </div>

            <div class="detail-input-group">
              <label for="event-date">EVENT START & TIME *</label>
              <input
                id="event-date"
                type="datetime-local"
                v-model="eventDate"
                class="custom-input date-picker"
                required
              />
            </div>

            <div class="form-row">
              <div class="detail-input-group">
                <label for="end-time">EVENT END & TIME</label>
                <input
                  id="end-time"
                  type="datetime-local"
                  v-model="endTime"
                  class="custom-input date-picker"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="detail-input-group">
                <label for="max-capacity">MAX CAPACITY</label>
                <input
                  id="max-capacity"
                  type="number"
                  v-model="maxCapacity"
                  placeholder="E.g. 500"
                  class="custom-input"
                />
              </div>
              <div class="detail-input-group">
                <label for="ticket-price">TICKET PRICE (€)</label>
                <input
                  id="ticket-price"
                  type="number"
                  step="0.01"
                  v-model="ticketPrice"
                  placeholder="E.g. 15.00"
                  class="custom-input"
                />
              </div>
            </div>

            <div class="detail-input-group">
              <label for="event-tags">TAGS</label>
              <input
                id="event-tags"
                type="text"
                v-model="eventTags"
                placeholder="E.g. party, club, dj"
                class="custom-input"
              />
            </div>

            <div class="detail-input-group">
              <label for="event-status">STATUS *</label>
              <select id="event-status" v-model="eventStatus" class="custom-input custom-select" required>
                <option value="Active">Active</option>
                <option value="Draft">Draft</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </div>

          </div>
        </div>

      </div>

      <div class="publish-action-bar">
        <button class="publish-btn" @click="handlePublish">
          PUBLISH EVENT
        </button>
      </div>
    </section>
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

.page-title {
  font-family: 'jf-openhuninn', 'Huninn', sans-serif !important;
  letter-spacing: 3px;
  text-transform: uppercase;
}

input,
select,
textarea,
button,
label,
h1, h2, h3, h4,
p, span, li, small,
.custom-input,
.action-btn-small,
.publish-btn,
.nav-visual-btn {
  font-family: 'jf-openhuninn', 'Huninn', sans-serif !important;
}

input::placeholder,
textarea::placeholder {
  font-family: 'jf-openhuninn', 'Huninn', sans-serif !important;
}

.logo,
.logo-text {
  font-family: "Bruno Ace", sans-serif !important;
  font-weight: bold;
  font-size: 1.2rem;
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
  max-width: 1550px;
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
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-visual-btn:hover {
  background: rgba(0, 242, 254, 0.2);
  border-color: #00f2fe;
  color: #00f2fe;
}

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 30px;
  width: calc(100% - 40px);
  max-width: 1550px;
  margin: 15px auto 0 auto;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  position: sticky;
  top: 15px;
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
  font-family: 'Bruno Ace', cursive, sans-serif;
  font-weight: 400;
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

.glass-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 25px;
  box-sizing: border-box;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: all 0.5s ease;
  max-width: 1550px;
  margin: 0 auto;
}

.preview-box {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 25px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 25px;
  flex-wrap: wrap;
}

/* STEP COLUMNS & STATES */
.step-column {
  display: flex;
  flex-direction: column;
  gap: 15px;
  transition: all 0.3s ease;
  cursor: pointer;
  opacity: 0.7;
}

.step-active {
  opacity: 1;
}

/* When active, content boxes print solid light blue outline border */
.step-active .map-container-inline,
.step-active .media-outer-wrapper,
.step-active .event-details-bar-vertical {
  border: 2px solid #00f2fe;
  box-shadow: 0 0 20px rgba(0, 242, 254, 0.25);
}

.step-header-label {
  font-size: 0.8rem;
  font-weight: bold;
  letter-spacing: 1px;
  color: rgba(255, 255, 255, 0.7);
  text-align: left;
  padding-left: 5px;
}

.right-section {
  width: 420px;
  flex-shrink: 0;
}

/* Transparent Glass Content Boxes Restored */
.event-details-bar-vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(0, 0, 0, 0.3);
  padding: 20px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  max-height: 680px;
  overflow-y: auto;
  cursor: default;
  transition: border 0.3s ease, box-shadow 0.3s ease;
}

.form-row {
  display: flex;
  gap: 10px;
}

.form-row .detail-input-group {
  flex: 1;
}

.detail-input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;
}

.detail-input-group label {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.75);
  letter-spacing: 0.5px;
}

.custom-input {
  width: 100%;
  box-sizing: border-box;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.3);
  color: #FFFFFF;
  font-size: 0.8rem;
  color-scheme: dark;
}

.textarea-input {
  resize: vertical;
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

.media-outer-wrapper {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 16px;
  backdrop-filter: blur(12px);
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 380px;
  height: 535px;
  flex-shrink: 0;
  cursor: default;
  transition: border 0.3s ease, box-shadow 0.3s ease;
}

.media-preview {
  border: 2px dashed rgba(255, 255, 255, 0.5);
  border-radius: 18px;
  width: 100%;
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

.media-preview.clickable {
  cursor: pointer;
}

.media-preview.clickable:hover {
  border-color: rgba(0, 242, 254, 0.8);
}

.uploaded-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  opacity: 0.85;
  transition: opacity 0.3s ease;
}

.map-container-inline {
  width: 380px;
  height: 535px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 16px;
  backdrop-filter: blur(12px);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  cursor: default;
  transition: border 0.3s ease, box-shadow 0.3s ease;
}

.map-inner-wrapper {
  border: 2px dashed rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.03);
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
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
  border-radius: 0 0 14px 14px;
  filter: invert(90%) hue-rotate(180deg) contrast(80%);
}

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

@media (max-width: 1200px) {
  .preview-box {
    flex-direction: column;
    align-items: center;
  }
  .right-section {
    width: 100%;
  }
  .map-container-inline,
  .media-outer-wrapper {
    width: 100%;
    max-width: 480px;
  }
}
</style>