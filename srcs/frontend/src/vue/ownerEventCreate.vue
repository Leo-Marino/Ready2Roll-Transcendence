<script>
import { t as $t } from '../i18n';
import NotificationBell from './NotificationBell.vue';
import ChatNavLink from './ChatNavLink.vue';
import { currentLang } from '../i18n';
import LanguageSwitcher from './LanguageSwitcher.vue';


export default {
  name: 'CreateEvent',
  components: { NotificationBell, ChatNavLink , LanguageSwitcher},
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
      eventStatus: 'draft',
      uploadedMediaSrc: null,
      actualFile: null,
      mediaType: null,
      showMapBox: false,
      availableTags: ['Disco', 'Trap', 'Hip Hop', 'Rock', 'Jazz'],
      selectedTags: [],
      tagsLoading: false,
      tagsError: '',
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
  },
  async mounted() {
    if (this.$route.query.edit === 'true') {
      const savedEvent = sessionStorage.getItem('editingEvent');
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
          this.eventStatus = ev.status ? ev.status.toLowerCase() : 'active';
          this.uploadedMediaSrc = ev.media_src || null;
          this.mediaType = ev.media_type || 'image';
          this.selectedTags = (Array.isArray(ev.tags) ? ev.tags : [])
            .map(tag => typeof tag === 'string' ? tag : tag.tag_name)
            .map(name => this.availableTags.find(
              k => k.toLowerCase() === String(name).toLowerCase()
            ))
            .filter(Boolean);
        } catch (e) {
          console.error('Error parsing editingEvent:', e);
        }
      }
    } else {
      sessionStorage.removeItem('editingEvent');
    }
  },
  methods: {
    async fetchAvailableTags() {
      this.tagsLoading = true;
      this.tagsError = '';
      try {
        const response = await fetch('/api/tags/');
        if (!response.ok) throw new Error(`Tags request failed (${response.status})`);
        const data = await response.json();
        this.availableTags = (Array.isArray(data) ? data : data.results || [])
          .map(tag => typeof tag === 'string' ? tag : tag.tag_name)
          .filter(Boolean);
      } catch (error) {
        console.error('Unable to load event tags:', error);
        this.tagsError = 'Could not load tags. Please refresh the page.';
      } finally {
        this.tagsLoading = false;
      }
    },
    toggleTag(tagName) {
      const index = this.selectedTags.findIndex(
        tag => tag.toLowerCase() === tagName.toLowerCase()
      );
      if (index >= 0) this.selectedTags.splice(index, 1);
      else this.selectedTags.push(tagName);
    },
    isTagSelected(tagName) {
      return this.selectedTags.some(
        tag => tag.toLowerCase() === tagName.toLowerCase()
      );
    },
    goToStep(stepNumber) {
      this.activeStep = stepNumber;
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    toggleMapBox() {
      this.showMapBox = !this.showMapBox;
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
        alert($t('allFieldsMandatory'));
        return;
      }
      if (!this.isEditMode && !this.actualFile) {
        alert($t('insertMediaAlert'));
        return;
      }

      if (this.maxCapacity !== '' && Number(this.maxCapacity) < 0) {
        alert($t('capacityNegative'));
        return;
      }
      if (this.ticketPrice !== '' && Number(this.ticketPrice) < 0) {
        alert($t('priceNegative'));
        return;
      }

      const token = sessionStorage.getItem('token') || sessionStorage.getItem('access') || sessionStorage.getItem('access_token');
      const formData = new FormData();

      formData.append('title', this.eventTitle);
      formData.append('description', this.descriptionText);
      formData.append('location', this.eventLocation);
      formData.append('event_date', this.eventDate);
      formData.append('status', this.eventStatus);
      // Send the selected tag names as one JSON array for the DRF serializer.
      this.selectedTags.forEach(tag => formData.append('tags', tag));

      if (this.maxCapacity) formData.append('max_capacity', this.maxCapacity);
      if (this.ticketPrice) formData.append('ticket_price', this.ticketPrice);
      if (this.endTime) formData.append('end_time', this.endTime);
      if (this.eventDate) {
        formData.append('start_time', this.eventDate);
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
          sessionStorage.removeItem('editingEvent');
          alert(this.isEditMode ? $t('eventUpdated') : (this.eventStatus === 'scheduled' ? $t('eventScheduled') : $t('eventCreated')));
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
        alert($t('networkError'));
      }
    },
    goToVisualPage() {
      sessionStorage.removeItem('editingEvent');
      if (this.$router) {
        this.$router.push('/profile');
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
      <div class="logo" @click="$router.push('/home')">
        <img src="../assets/logo_temp.png" alt="Ready2Roll Logo" class="nav-logo-img">
        <span class="logo-text">Ready2Roll</span>
      </div>
      <div class="nav-icons">
        <LanguageSwitcher />
        <NotificationBell />
        <router-link to="/chat" class="nav-icon-link">
          <ChatNavLink>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
          </ChatNavLink>
        </router-link>
        <router-link to="/profile" class="nav-icon-link">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="nav-icon">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
        </router-link>
      </div>
    </header>

  <main class="main-content">
    <div class="page-title-row">
      <h1 class="page-title">{{ isEditMode ? $t('editEventTitle') : $t('createEventTitle') }}</h1>
      <button class="action-btn nav-visual-btn" @click="goToVisualPage">
          {{ $t('myEvents') }}
      </button>
    </div>

    <section class="glass-card">
      <div class="preview-box">

        <!-- STEP 1: CONTENT MEDIA -->
        <div class="step-column" :class="{ 'step-active': activeStep === 1 }" @click="goToStep(1)">
          <div class="step-header-label">{{ $t('contentMedia') }}</div>
          <div class="media-outer-wrapper">
            <div
              class="media-preview clickable"
              :class="{ 'has-content': uploadedMediaSrc }"
            >
              <!-- Map Toggle Button -->
              <button type="button" class="media-map-toggle-btn" @click.stop="toggleMapBox">
                {{ showMapBox ? $t('hideMap') : $t('viewMap') }}
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
                  <span>{{ $t('insertMedia') }}</span>
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
            <div class="step-header-label">{{ $t('mapLocation') }}</div>
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
          <div class="step-header-label">{{ $t('eventDetails') }}</div>
          <div class="event-details-bar-vertical">

            <div class="detail-input-group">
              <label for="event-title">{{ $t('titleLabel') }}</label>
              <input
                id="event-title"
                type="text"
                v-model="eventTitle"
                :placeholder="$t('titlePlaceholder')"
                class="custom-input"
                required
              />
            </div>

            <div class="detail-input-group">
              <label for="event-description">{{ $t('descriptionLabel') }}</label>
              <textarea
                id="event-description"
                v-model="descriptionText"
                :placeholder="$t('descriptionPlaceholder')"
                class="custom-input textarea-input"
                rows="1"
                required
              ></textarea>
            </div>

            <div class="detail-input-group">
              <label for="event-location">{{ $t('locationLabel') }}</label>
              <input
                id="event-location"
                type="text"
                :placeholder="$t('locationPlaceholder')"
                class="custom-input map-input"
                v-model="eventLocation"
              />
            </div>

            <div class="detail-input-group">
              <label for="event-date">{{ $t('eventStart') }}</label>
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
                <label for="end-time">{{ $t('eventEnd') }}</label>
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
                <label for="max-capacity">{{ $t('maxCapacityLabel') }}</label>
                <input
                  id="max-capacity"
                  type="number"
                  min="0"
                  v-model="maxCapacity"
                  :placeholder="$t('capacityPlaceholder')"
                  class="custom-input"
                />
              </div>
              <div class="detail-input-group">
                <label for="ticket-price">{{ $t('ticketPriceLabel') }}</label>
                <input
                  id="ticket-price"
                  type="number"
                  step="0.01"
                  min="0"
                  v-model="ticketPrice"
                  :placeholder="$t('pricePlaceholder')"
                  class="custom-input"
                />
              </div>
            </div>

            <div class="detail-input-group">
              <label for="event-status">{{ $t('statusLabel') }}</label>
              <select id="event-status" v-model="eventStatus" class="custom-input custom-select" required>
                <option value="active">{{ $t('statusActive') }}</option>
                <option value="draft">{{ $t('statusDraft') }}</option>
                <option value="scheduled">{{ $t('statusScheduled') }}</option>
              </select>
            </div>

            <!-- TAGS POSTI SOTTO ALLO STATUS -->
            <div class="detail-input-group event-tags-group">
              <div class="tags-heading-row">
                <label>{{ $t('tagsLabel') }}</label>
                <span class="tags-count">{{ selectedTags.length }} selected</span>
              </div>

              <p v-if="tagsLoading" class="tags-hint">Loading tags...</p>
              <p v-else-if="tagsError" class="tags-error">{{ tagsError }}</p>
              <div v-else-if="availableTags.length" class="tag-selector-container">
                <button
                  v-for="t in availableTags"
                  :key="t"
                  type="button"
                  @click.stop="toggleTag(t)"
                  :class="isTagSelected(t) ? 'business-badge' : 'standard-badge'"
                  class="selectable-tag-pill"
                  :aria-pressed="isTagSelected(t)"
                >
                  <span class="tag-pill-icon">{{ isTagSelected(t) ? '✓' : '+' }}</span>
                  <span>{{ t }}</span>
                </button>
              </div>
              <p v-else class="tags-hint">No tags are available yet.</p>
            </div>

          </div>
        </div>

      </div>

      <div class="publish-action-bar">
      <button class="publish-btn" @click="handlePublish">
        {{ isEditMode ? $t('saveChanges') : (eventStatus === 'scheduled' ? $t('scheduleEvent') : $t('publishEvent')) }}
      </button>
      </div>
    </section>
  </main>
</div>
</template>

<style scoped>

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
  font-family: var(--font-main);
  box-sizing: border-box;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.page-title {
  font-family: var(--font-main) !important;
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
  font-family: var(--font-main) !important;
}

input::placeholder,
textarea::placeholder {
  font-family: var(--font-main) !important;
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
  width: 100%; /* Badlna width: calc(100% - 40px) b 100% */
  max-width: 1550px;
  margin: 15px auto;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  flex-shrink: 0;
}

/* Zid had l'fix 3la wed RTL Navbar */
[dir="rtl"] .navbar {
  flex-direction: row-reverse;
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
  font-family: "Bruno Ace", sans-serif;
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
  height: 590px;
  overflow-y: auto;
  scrollbar-width: none;
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
  height: 590px;
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
  height: 590px;
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

/* Event tags: same Ready2Roll glass + cyan badge style as the profile page */
.event-tags-group {
  margin-top: 4px;
  padding-top: 9px;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
}

.tags-heading-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.tags-count,
.tags-hint {
  color: rgba(255, 255, 255, 0.58);
  font-size: 0.62rem;
}

.tag-selector-container {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 7px;
}

.selectable-tag-pill {
  appearance: none;
  cursor: pointer;
  user-select: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 14px;
  font: inherit;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.35px;
  text-transform: uppercase;
  backdrop-filter: blur(5px);
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.selectable-tag-pill:hover {
  transform: translateY(-2px);
}

.business-badge {
  background: rgba(0, 242, 254, 0.16);
  border: 1px solid #00f2fe;
  color: #00f2fe;
  box-shadow: 0 0 9px rgba(0, 242, 254, 0.22);
}

.standard-badge {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.28);
  color: rgba(255, 255, 255, 0.82);
}

.tag-pill-icon {
  font-size: 0.8rem;
  line-height: 1;
}

.tags-error {
  color: #ff9292;
  font-size: 0.65rem;
}

/* RTL Fixes for Create Event Page */
[dir="rtl"] .preview-box {
  flex-direction: row-reverse; /* Hada kiy-qleb l'columns f RTL bach tb9a l'Media 3la l'iser w details 3la limn (aw l'3ekss kima bghiti) */
  justify-content: space-between; /* Hada kiy-ferreqhom 3la b3diyathom */
  gap: 30px; /* Zidna chwya f l'espace binathom f RTL */
}

/* Ila bghiti tfiy-fixer 7ta l'titles dyalhom bach ib9aw m9addin f RTL */
[dir="rtl"] .step-header-label {
  text-align: right;
  padding-right: 5px;
  padding-left: 0;
}

/* L'inputs dyal l'details khasshom ijiw mn l'imin l'isser f RTL */
[dir="rtl"] .detail-input-group {
  text-align: right;
}

[dir="rtl"] .custom-input {
  text-align: right;
}

[dir="rtl"] .form-row {
  flex-direction: row-reverse; /* Hada kiy-qleb "Max Capacity" w "Ticket Price" f RTL */
}

[dir="rtl"] .tag-selector-container {
  justify-content: flex-end; /* Tags kiybano mn limin */
}

</style>
