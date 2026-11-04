// src/stores/notificationStore.js
import { defineStore } from 'pinia';

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: [],
    unreadCount: 0,
    socket: null,
  }),
  actions: {
    getToken() {
      return localStorage.getItem('token') || localStorage.getItem('access') || localStorage.getItem('access_token');
    },

	async fetchNotifications() {
		const token = this.getToken();
		if (!token) return;
		try {
		  const res = await fetch('/api/notifications/', {
			headers: { 'Authorization': `Bearer ${token}` }
		  });
		  if (res.ok) {
			const data = await res.json();
			// FIX: Aggiunto "|| []" e "|| 0" come paracadute
			this.notifications = data.notifications || [];
			this.unreadCount = data.unread_count || 0;
		  }
		} catch (error) {
		  console.error("Errore fetch notifiche", error);
		  // Resetta i valori in caso di errore di rete
		  this.notifications = [];
		  this.unreadCount = 0;
		}
	  },
    async markAsRead() {
      if (this.unreadCount === 0) return;
      const token = this.getToken();
      try {
        await fetch('/api/notifications/read/', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        this.unreadCount = 0;
        this.notifications.forEach(n => n.is_read = true);
      } catch (error) {
        console.error("Errore mark as read", error);
      }
    },

    connectWebSocket() {
      const token = this.getToken();
      // Evita di aprire connessioni multiple se il socket esiste già
      if (!token || this.socket) return;

      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      // Nel backend la rotta richiede un ID utente per la chat, mettiamo 0 come fallback generico
      // tanto il token JWT identifica l'utente reale nel middleware
      const wsUrl = `${wsProtocol}//${window.location.host}/ws/chat/0/?token=${token}`;

      this.socket = new WebSocket(wsUrl);

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'notification') {
          this.notifications.unshift(data.notification);
          this.unreadCount++;
        }
      };

      this.socket.onclose = () => {
        this.socket = null; // Resetta se si chiude
      };
    },

    disconnectWebSocket() {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
    }
  }
});
