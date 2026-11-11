import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useSocialSocket } from './useSocialSocket';

// Number of unread direct messages, shared by every navbar that shows the chat icon.
// Updated live: the server pushes { action: 'message' } through the social socket
// whenever a message arrives (or gets read from another tab). We then ask the
// backend for the fresh count, so the number is never computed on the client.

const API = '/api';
const unreadMessages = ref(0);

const getToken = () =>
  sessionStorage.getItem('token') || sessionStorage.getItem('access') || sessionStorage.getItem('access_token');

const fetchUnreadMessages = async () => {
  const token = getToken();
  if (!token) return;
  try {
    const res = await fetch(`${API}/social/messages/unread-count/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) unreadMessages.value = (await res.json()).count;
  } catch (e) { /* network down: the next event will refresh it */ }
};

// Call inside <script setup>
export function useUnreadMessages() {
  useSocialSocket((message) => {
    if (message.action === 'message' || message.action === 'resync') fetchUnreadMessages();
  });

  // A hidden tab may have missed updates: catch up as soon as it is visible again
  const onVisibilityChange = () => {
    if (!document.hidden) fetchUnreadMessages();
  };

  onMounted(() => {
    fetchUnreadMessages();
    document.addEventListener('visibilitychange', onVisibilityChange);
  });
  onBeforeUnmount(() => {
    document.removeEventListener('visibilitychange', onVisibilityChange);
  });

  return { unreadMessages, hasUnread: computed(() => unreadMessages.value > 0) };
}
