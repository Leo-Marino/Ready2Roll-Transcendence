import { onBeforeUnmount } from 'vue';
const MAX_RETRY_DELAY_MS = 30000;

const listeners = new Set();
let socket = null;
let reconnectTimer = null;
let retryCount = 0;
let hasConnectedBefore = false;
let wantOpen = false;

const getToken = () =>
  sessionStorage.getItem('token') || sessionStorage.getItem('access') || sessionStorage.getItem('access_token');

const dispatch = (message) => {
  listeners.forEach((listener) => {
    try {
      listener(message);
    } catch (error) {
      // console.error('Social socket listener failed:', error);
    }
  });
};

const scheduleReconnect = () => {
  if (!wantOpen || reconnectTimer) return;
  const delay = Math.min(1000 * 2 ** retryCount, MAX_RETRY_DELAY_MS);
  retryCount += 1;
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    connect();
  }, delay);
};

const connect = () => {
  const token = getToken();
  if (!wantOpen || !token) return;
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) return;

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  socket = new WebSocket(`${protocol}//${window.location.host}/ws/social/?token=${token}`);

  socket.onopen = () => {
    retryCount = 0;
    if (hasConnectedBefore) dispatch({ action: 'resync', target_id: null, data: {} });
    hasConnectedBefore = true;
  };

  socket.onmessage = (event) => {
    try {
      dispatch(JSON.parse(event.data));
    } catch (error) {
    }
  };

  socket.onclose = () => {
    socket = null;
    scheduleReconnect();
  };

  socket.onerror = () => {
    // onclose is always fired after onerror: the reconnection is handled there
  };
};

const disconnect = () => {
  wantOpen = false;
  hasConnectedBefore = false;
  retryCount = 0;
  clearTimeout(reconnectTimer);
  reconnectTimer = null;
  if (socket) {
    socket.onclose = null;
    socket.close();
    socket = null;
  }
};

// Call inside <script setup>. `handler` receives every message.
export function useSocialSocket(handler) {
  listeners.add(handler);
  wantOpen = true;
  connect();

  onBeforeUnmount(() => {
    listeners.delete(handler);
    if (listeners.size === 0) disconnect();
  });
}
