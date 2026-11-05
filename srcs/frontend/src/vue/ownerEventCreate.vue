<script>
import NotificationBell from './NotificationBell.vue';
import ChatNavLink from './ChatNavLink.vue';

export default {
  name: 'CreateEvent',
  components: { NotificationBell, ChatNavLink },
  emits: ['navigate-view', 'event-published'],
  data() {
    return {
      isEditMode: false,
      editingEventId: null,
      activeStep: 1,
      eventTitle: '',
      descriptionText: '',
      eventLocation: 'YAB Club, Florence',
      eventDate: '',
      maxCapacity: '',
      ticketPrice: '',
      startTime:'',
      endTime: '',
      tags: '',
      availableTags: ['Disco', 'Strip', 'DJ', 'Rave', 'Nostalgia', 'VIP', 'Cocktail', '420'],
      eventStatus: 'draft',
      uploadedMediaSrc: null,
      actualFile: null,
      mediaType: null,
      showMapBox: false
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
    },
    selectedTagsList() {
      if (!this.tags) return [];
      return this.tags.split(',').map(t => t.trim()).filter(Boolean);
    }
  },
  mounted() {
    if (this.$route.query.edit === 'true') {
      const savedEvent = localStorage.getItem('editingEvent');
      if (savedEvent) {
        try {
          const ev = JSON.parse(savedEvent);
          this.isEditMode = true;
          this.editingEventId = ev.id;
          this.eventTitle = ev.title || '';
          this.descriptionText = ev.description || '';
          this.eventLocation = ev.location || 'YAB Club, Florence';
          this.eventDate = ev.event_date ? String(ev.event_date).slice(0, 16) : '';
          this.startTime = this.eventDate;
          this.endTime = ev.end_time ? String(ev.end_time).slice(0, 16) : '';
          this.maxCapacity = ev.max_capacity || '';
          this.ticketPrice = ev.ticket_price || '';
          this.tags = Array.isArray(ev.tags) ? ev.tags.join(', ') : (ev.tags || '');
          this.eventStatus = ev.status ? ev.status.toLowerCase() : 'active';
          this.uploadedMediaSrc = ev.media_src || null;
          this.mediaType = ev.media_type || 'image';
        } catch (e) {
          console.error('Error parsing editingEvent:', e);
        }
      }
    } else {
      localStorage.removeItem('editingEvent');
    }
  },
  methods: {
    goToStep(stepNumber) {
      this.activeStep = stepNumber;
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    toggleMapBox() {
      this.showMapBox = !this.showMapBox;
    },
    toggleTag(tagName) {
      let currentTags = this.selectedTagsList;
      if (currenttagsIncludes(currentTags, tagName)) {
        currentTags = currentTags.filter(t => t.toLowerCase() !== tagName.toLowerCase());
      } else {
        currentTags.push(tagName);
      }
      this.tags = currentTags.join(', ');
    },
    isTagSelected(tagName) {
      return this.selectedTagsList.some(t => t.toLowerCase() === tagName.toLowerCase());
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
    clearMedia() {
      this.uploadedMediaSrc = null;
      this.actualFile = null;
      this.mediaType = null;
    },
    async handlePublish() {
      if (!this.eventTitle || !this.descriptionText || !this.eventDate || !this.eventStatus) {
        alert("All mandatory fields must be filled !");
        return;
      }
      if (!this.isEditMode && !this.actualFile) {
        alert("Please insert a photo or video before publishing the event!");
        return;
      }

      // Controllo valori negativi per Max Capacity e Ticket Price
      if (this.maxCapacity !== '' && Number(this.maxCapacity) < 0) {
        alert("Max capacity cannot be less than 0!");
        return;
      }
      if (this.ticketPrice !== '' && Number(this.ticketPrice) < 0) {
        alert("Ticket price cannot be less than 0!");
        return;
      }

      const token = localStorage.getItem('token') || localStorage.getItem('access') || localStorage.getItem('access_token');
      const formData = new FormData();

      formData.append('title', this.eventTitle);
      formData.append('description', this.descriptionText);
      formData.append('location', this.eventLocation);
      formData.append('event_date', this.eventDate);
      formData.append('status', this.eventStatus);

      if (this.maxCapacity) formData.append('max_capacity', this.maxCapacity);
      if (this.ticketPrice) formData.append('ticket_price', this.ticketPrice);
      if (this.endTime) formData.append('end_time', this.endTime);
      if (this.eventDate) {
        formData.append('start_time', this.eventDate);
      }
      //------------------------------------------
      if (this.tags) {
        const tagsArray = this.tags.split(',').map(tag => tag.trim()).filter(Boolean);
        tagsArray.forEach(tag => {
          formData.append('tags', tag);
        });
      }

      if (this.actualFile) {
        formData.append('media_file', this.actualFile);
        formData.append('media_type', this.mediaType);
      } else if (this.mediaType) {
        formData.append('media_type', this.mediaType);
      }

      const url = this.isEditMode ? `/api/events/${this.editingEventId}/` : '/api/events/';
      const method = this.isEditMode ? 'PUT' : 'POST';

      try {
        const response = await fetch(url, {
          method: method,
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });

        if (response.ok) {
          const savedEvent = await response.json();
          localStorage.removeItem('editingEvent');
          alert(this.isEditMode ? "Event updated successfully!" : (this.eventStatus === 'scheduled' ? "Event scheduled successfully!" : "Event created successfully!"));
          this.$emit('event-published', savedEvent);
          this.goToVisualPage();
        }
        else if (response.status === 401) {
          alert("Unauthorized user; please log in again");
          this.$router.push('/login');
        }
        else if (response.status === 400) {
          const errorData = await response.json();
          console.error("Validation error: ", errorData);
          alert("A validation error was found; please check your input");
        }
        else {
          const errorData = await response.json();
          console.error("Backend error:", errorData);
          alert("There was an error saving the event");
        }
      } catch (error) {
        console.error("Network error", error);
        alert("Unable to connect to the backend server");
      }
    },
    goToVisualPage() {
      localStorage.removeItem('editingEvent');
      if (this.$router) {
        this.$router.push('/profile');
      }
      this.$emit('navigate-view');
    }
  }
}

// Helper interno per la ricerca dei tag selezionati
function currenttagsIncludes(arr, val) {
  return arr.some(t => t.toLowerCase() === val.toLowerCase());
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
        <NotificationBell />
        <ChatNavLink>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
          </svg>
        </ChatNavLink>
        <!-- <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 011.037-.443 48.282 48.282 0 005.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
        </svg> -->
        <router-link to="/profile" class="nav-icon-link">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
        </router-link>
      </div>
    </div>
  </header>

  <main class="main-content">
    <div class="page-title-row">
      <h1 class="page-title">{{ isEditMode ? 'EDIT EVENT' : 'CREATE AN EVENT' }}</h1>
      <button class="action-btn nav-visual-btn" @click="goToVisualPage">
        📂 MY EVENTS
      </button>
    </div>

    <section class="glass-card">
      <div class="preview-box">

        <!-- STEP 1: CONTENT MEDIA -->
        <div class="step-column" :class="{ 'step-active': activeStep === 1 }" @click="goToStep(1)">
          <div class="step-header-label">1. CONTENT MEDIA</div>
          <div class="media-outer-wrapper">
            <div
              class="media-preview clickable"
              :class="{ 'has-content': uploadedMediaSrc }"
            >
              <!-- Map Toggle Button -->
              <button type="button" class="media-map-toggle-btn" @click.stop="toggleMapBox">
                {{ showMapBox ? '🗺️ Hide map' : '🗺️ View map' }}
              </button>

              <!-- Remove Media Button (Only shows when file is uploaded) -->
              <button
                v-if="uploadedMediaSrc"
                type="button"
                class="media-remove-btn"
                @click.stop="clearMedia"
                title="Remove media"
              >
                ✕
              </button>

              <div @click="triggerFileInput" class="media-inner-click-area">
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
        </div>

        <!-- STEP 2: MAP LOCATION (Animated transition wrapper) -->
        <transition name="map-slide">
          <div class="step-column" v-if="showMapBox" :class="{ 'step-active': activeStep === 2 }" @click="goToStep(2)">
            <div class="step-header-label">2. MAP LOCATION</div>
            <div class="map-container-inline">
              <div class="map-inner-wrapper">
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
        </transition>

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
                rows="1"
                required
              ></textarea>
            </div>

            <div class="detail-input-group">
              <label for="event-location">LOCATION *</label>
              <input
                id="event-location"
                type="text"
                placeholder="Find desired address or location"
                class="custom-input map-input"
                v-model="eventLocation"
              />
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
            <!-- <input
              id="event-date"
              type="datetime-local"
              v-model="eventDate"
              class="custom-input date-picker"
              required
            /> -->
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
                  min="0"
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
                  min="0"
                  v-model="ticketPrice"
                  placeholder="E.g. 15.00"
                  class="custom-input"
                />
              </div>
            </div>

            <!-- STATUS POSTO PRIMA DEI TAGS -->
            <div class="detail-input-group">
              <label for="event-status">STATUS *</label>
              <select id="event-status" v-model="eventStatus" class="custom-input custom-select" required>
                <option value="active">Active</option>
                <option value="draft">Draft</option>
                <option value="scheduled">Scheduled</option>
              </select>
            </div>

            <!-- TAGS POSTI SOTTO ALLO STATUS -->
            <div class="detail-input-group">
              <label>TAGS</label>
              <div class="tag-selector-container">
                <div
                  v-for="t in availableTags"
                  :key="t"
                  @click="toggleTag(t)"
                  :class="isTagSelected(t) ? 'business-badge' : 'standard-badge'"
                  class="selectable-tag-pill"
                >
                  <span>{{ isTagSelected(t) ? '✓' : '+' }}</span>
                  <span>{{ t }}</span>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>

      <div class="publish-action-bar">
        <button class="publish-btn" @click="handlePublish">
          {{ isEditMode ? 'SAVE CHANGES' : (eventStatus === 'scheduled' ? 'SCHEDULE EVENT' : 'PUBLISH EVENT') }}
        </button>
      </div>
    </section>
  </main>
</div>
</template>

<style scoped>
@import url('https://cdn.jsdelivr.net/gh/justfont/open-huninn-font@1.1/font/jf-openhuninn.css');

html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.owner-visual-wrapper {
  position: relative;
  height: 100vh;
  width: 100vw;
  color: #ffffff;
  font-family: 'jf-openhuninn', 'Huninn', sans-serif;
  box-sizing: border-box;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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
  overflow: hidden;
}

.page-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1550px;
  margin: 0 auto 15px auto;
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
  margin: 15px auto 15px auto;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  flex-shrink: 0;
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
  width: 380px;
  flex-shrink: 0;
}

/* Smooth Map Slide/Fade Transition Styles */
.map-slide-enter-active,
.map-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  max-width: 380px;
  opacity: 1;
  overflow: hidden;
}

.map-slide-enter-from,
.map-slide-leave-to {
  opacity: 0;
  max-width: 0;
  transform: scaleX(0);
  margin-left: 0;
  margin-right: 0;
  padding-left: 0;
  padding-right: 0;
}

/* Event Details Box - Spaziatura aumentata e field ingranditi */
.event-details-bar-vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(255, 255, 255, 0.08);
  padding: 18px 16px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(12px);
  width: 380px;
  height: 525px;
  box-sizing: border-box;
  overflow: hidden;
  cursor: default;
  transition: border 0.3s ease, box-shadow 0.3s ease;
}

.form-row {
  display: flex;
  gap: 12px;
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
  font-size: 0.65rem;
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
  resize: none;
  min-height: 36px;
  max-height: 36px;
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

/* Media Outer Wrapper - Altezza perfettamente identica a event details (525px) */
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
  height: 525px;
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

.media-inner-click-area {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  font-size: 0.8rem;
}

.media-map-toggle-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid #00f2fe;
  color: #00f2fe;
  padding: 5px 10px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: bold;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: all 0.3s ease;
}

.media-map-toggle-btn:hover {
  background: #00f2fe;
  color: #000;
}

.media-remove-btn {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  background: rgba(214, 48, 49, 0.8);
  border: 1px solid #ff7675;
  color: #ffffff;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: all 0.3s ease;
}

.media-remove-btn:hover {
  background: #d63031;
  transform: scale(1.1);
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
  height: 525px;
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

.map-iframe {
  flex-grow: 1;
  width: 100%;
  height: 100%;
  border-radius: 14px;
  filter: invert(90%) hue-rotate(180deg) contrast(80%);
}

.publish-action-bar {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.publish-btn {
  background: rgba(0, 242, 254, 0.2);
  border: 1px solid #00f2fe;
  color: #00f2fe;
  padding: 12px 35px;
  font-size: 0.9rem;
  font-weight: bold;
  border-radius: 12px;
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

/* Tag Selector Box Styles */
.tag-selector-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 2px;
}

.selectable-tag-pill {
  cursor: pointer;
  user-select: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.selectable-tag-pill:hover {
  transform: translateY(-1px);
}

.business-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(0, 242, 254, 0.15);
  border: 1px solid #00f2fe;
  color: #00f2fe;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: bold;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  backdrop-filter: blur(4px);
  box-shadow: 0 0 6px rgba(0, 242, 254, 0.2);
}

.standard-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.85);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: bold;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  backdrop-filter: blur(4px);
}

@media (max-width: 1200px) {
  .preview-box {
    flex-direction: column;
    align-items: center;
  }
  .right-section,
  .event-details-bar-vertical {
    width: 100%;
    max-width: 480px;
    height: auto;
  }
  .map-container-inline,
  .media-outer-wrapper {
    width: 100%;
    max-width: 480px;
    height: 440px;
  }
}
</style>
