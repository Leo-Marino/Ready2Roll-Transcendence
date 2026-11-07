<script setup>
import { useUnreadMessages } from '../composables/useUnreadMessages';

// Chat icon of the navbar + red dot when there are unread messages.
// The icon itself is passed by the page through the default slot.
defineProps({ title: { type: String, default: 'Chat' } });
const { hasUnread } = useUnreadMessages();
</script>

<template>
  <router-link to="/chat" class="nav-icon-link chat-link" :title="title">
    <slot />
    <span v-if="hasUnread" class="chat-dot" aria-label="Unread messages"></span>
  </router-link>
</template>

<style scoped>
.chat-link { position: relative; }
.chat-dot {
  position: absolute; top: -3px; right: -4px; width: 11px; height: 11px; box-sizing: border-box;
  border-radius: 50%; background: #ff3b5c; border: 2px solid rgba(20, 10, 40, 0.9);
  box-shadow: 0 0 8px rgba(255, 59, 92, 0.7); pointer-events: none;
}
</style>
