<script setup>
import { ref } from 'vue';

// Shared grid of event videos/images, used by the owner profile and
// by the profile that other users see.
defineProps({
  events: { type: Array, default: () => [] },
  emptyText: { type: String, default: 'No videos yet.' },
  showStatus: { type: Boolean, default: false },
});

const selected = ref(null);

const open = (event) => { selected.value = event; };
const close = () => { selected.value = null; };

// Play a preview while hovering a card
const hoverPlay = (e) => { const v = e.currentTarget.querySelector('video'); if (v) v.play().catch(() => {}); };
const hoverStop = (e) => {
  const v = e.currentTarget.querySelector('video');
  if (v) { v.pause(); v.currentTime = 0.1; }
};

const formatDate = (iso) => {
  if (!iso) return '';
  return new Date(iso).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
};
</script>

<template>
  <p v-if="events.length === 0" class="glass-panel empty-msg">{{ emptyText }}</p>

  <div v-else class="video-grid">
    <div
      class="video-card glass-panel"
      v-for="event in events"
      :key="event.id"
      @click="open(event)"
      @mouseenter="hoverPlay"
      @mouseleave="hoverStop"
    >
      <img v-if="event.media_type === 'image' && event.media_src" :src="event.media_src" :alt="event.title" class="card-media">
      <video
        v-else-if="event.media_src"
        :src="event.media_src + '#t=0.1'"
        class="card-media"
        muted loop playsinline preload="metadata"
      ></video>
      <p v-else class="placeholder-text">no media</p>

      <span v-if="showStatus" class="status-badge" :class="(event.status || '').toLowerCase()">{{ event.status }}</span>
      <div class="card-title">{{ event.title }}</div>
    </div>
  </div>

  <!-- Enlarged viewer -->
  <div v-if="selected" class="viewer-overlay" @click.self="close">
    <div class="viewer">
      <button class="viewer-close" @click="close" aria-label="Close">✕</button>
      <div class="viewer-media">
        <img v-if="selected.media_type === 'image' && selected.media_src" :src="selected.media_src" :alt="selected.title">
        <video v-else-if="selected.media_src" :src="selected.media_src" controls autoplay loop playsinline></video>
      </div>
      <div class="viewer-info">
        <h3>{{ selected.title }}</h3>
        <p class="viewer-meta">
          <span v-if="selected.event_date" class="meta-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ui-icon lucide lucide-calendar-days">
              <path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/>
              <path d="M3 9h18"/><path d="M8 13h.01"/><path d="M12 13h.01"/><path d="M16 13h.01"/>
              <path d="M8 17h.01"/><path d="M12 17h.01"/><path d="M16 17h.01"/>
            </svg>
            {{ formatDate(selected.event_date) }}
          </span>
          <span v-if="selected.location" class="meta-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ui-icon lucide lucide-map-pin">
              <path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            {{ selected.location }}
          </span>
          <span v-if="selected.ticket_price" class="meta-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ui-icon lucide lucide-ticket">
              <path d="M15 5v2"/><path d="M15 11v2"/><path d="M15 17v2"/><path d="M5 5h14a2 2 0 0 1 2 2v3a2 2 0 0 0 0 4v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3a2 2 0 0 0 0-4v-3a2 2 0 0 1 2-2z"/>
            </svg>
            €{{ selected.ticket_price }}
          </span>
        </p>
        <p class="viewer-desc">{{ selected.description }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.glass-panel { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 15px; box-sizing: border-box; }
.empty-msg { text-align: center; color: rgba(255,255,255,0.7); }
.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
.video-card { aspect-ratio: 9 / 16; position: relative; overflow: hidden; padding: 0; cursor: pointer; display: flex; justify-content: center; align-items: center; transition: transform 0.2s; }
.video-card:hover { transform: scale(1.02); }
.card-media { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.placeholder-text { font-family: "Bruno Ace", sans-serif; opacity: 0.5; }
.card-title { position: absolute; left: 0; right: 0; bottom: 0; padding: 25px 12px 10px; font-weight: bold; font-size: 14px; background: linear-gradient(transparent, rgba(0,0,0,0.75)); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.status-badge { position: absolute; top: 10px; left: 10px; font-size: 11px; font-weight: bold; text-transform: uppercase; padding: 3px 8px; border-radius: 8px; background: rgba(0,0,0,0.6); }
.status-badge.active { background: rgba(0, 200, 120, 0.8); }
.status-badge.draft { background: rgba(120, 120, 120, 0.8); }
.status-badge.scheduled { background: rgba(255, 170, 0, 0.85); color: #000; }

.viewer-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.75); z-index: 1000; display: flex; justify-content: center; align-items: center; }
.viewer { position: relative; display: flex; gap: 20px; max-width: 900px; max-height: 90vh; padding: 20px; border-radius: 18px; background: rgba(20,20,30,0.95); color: white; }
.viewer-close { position: absolute; top: 10px; right: 14px; background: none; border: none; color: white; font-size: 20px; cursor: pointer; z-index: 2; }
.viewer-media { height: min(80vh, 640px); aspect-ratio: 9 / 16; background: #000; border-radius: 12px; overflow: hidden; flex-shrink: 0; }
.viewer-media img, .viewer-media video { width: 100%; height: 100%; object-fit: contain; }
.viewer-info { width: 280px; overflow-y: auto; }
.viewer-info h3 { margin-top: 10px; }
.viewer-meta { display: flex; flex-direction: column; gap: 6px; font-size: 14px; color: rgba(255,255,255,0.8); }
.viewer-desc { white-space: pre-wrap; word-break: break-word; line-height: 1.4; }
@media (max-width: 700px) { .viewer { flex-direction: column; overflow-y: auto; } .viewer-info { width: auto; } }

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.ui-icon {
  color: #00f2fe;
  flex-shrink: 0;
}
</style>
