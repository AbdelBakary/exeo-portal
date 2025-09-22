/**
 * Service WebSocket pour la réception d'alertes en temps réel
 */

class AlertWebSocket {
  constructor() {
    this.ws = null;
    this.callbacks = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 5000; // 5 secondes
    this.isConnected = false;
  }

  connect() {
    try {
      // URL du WebSocket (à adapter selon l'environnement)
      const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/alerts/';
      
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('🔌 WebSocket connecté');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        // Envoyer un ping pour vérifier la connexion
        this.send({
          type: 'ping',
          timestamp: new Date().toISOString()
        });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('❌ Erreur parsing message WebSocket:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket déconnecté:', event.code, event.reason);
        this.isConnected = false;
        
        // Tentative de reconnexion automatique
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`🔄 Tentative de reconnexion ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
          
          setTimeout(() => {
            this.connect();
          }, this.reconnectInterval);
        } else {
          console.error('❌ Nombre maximum de tentatives de reconnexion atteint');
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ Erreur WebSocket:', error);
      };

    } catch (error) {
      console.error('❌ Erreur création WebSocket:', error);
    }
  }

  handleMessage(data) {
    switch (data.type) {
      case 'alert':
        this.handleNewAlert(data);
        break;
      case 'integration_status':
        this.handleIntegrationStatus(data);
        break;
      case 'pong':
        console.log('🏓 Pong reçu du serveur');
        break;
      case 'subscribed':
        console.log('✅ Abonnement confirmé');
        break;
      case 'error':
        console.error('❌ Erreur serveur:', data.message);
        break;
      default:
        console.log('📨 Message WebSocket reçu:', data);
    }
  }

  handleNewAlert(alertData) {
    console.log('🚨 Nouvelle alerte reçue:', alertData);
    
    // Notifier tous les callbacks enregistrés
    this.callbacks.forEach(callback => {
      try {
        callback('alert', alertData);
      } catch (error) {
        console.error('❌ Erreur callback alerte:', error);
      }
    });

    // Afficher une notification toast
    this.showAlertNotification(alertData);
  }

  handleIntegrationStatus(statusData) {
    console.log('📊 Mise à jour statut intégration:', statusData);
    
    // Notifier les callbacks
    this.callbacks.forEach(callback => {
      try {
        callback('integration_status', statusData);
      } catch (error) {
        console.error('❌ Erreur callback statut:', error);
      }
    });
  }

  showAlertNotification(alertData) {
    // Vérifier si les notifications sont supportées
    if ('Notification' in window && Notification.permission === 'granted') {
      const notification = new Notification(`🚨 Nouvelle alerte - ${alertData.client}`, {
        body: `${alertData.title} (Score: ${alertData.risk_score})`,
        icon: '/favicon.ico',
        tag: alertData.alert_id,
        requireInteraction: true
      });

      notification.onclick = () => {
        window.focus();
        // Optionnel: naviguer vers la page des alertes
        window.location.href = '/alerts';
        notification.close();
      };

      // Fermer automatiquement après 10 secondes
      setTimeout(() => {
        notification.close();
      }, 10000);
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('⚠️ WebSocket non connecté, impossible d\'envoyer:', data);
    }
  }

  subscribe(callback) {
    this.callbacks.push(callback);
    
    // Envoyer un message d'abonnement
    this.send({
      type: 'subscribe',
      timestamp: new Date().toISOString()
    });
  }

  unsubscribe(callback) {
    const index = this.callbacks.indexOf(callback);
    if (index > -1) {
      this.callbacks.splice(index, 1);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.callbacks = [];
  }

  // Demander la permission pour les notifications
  async requestNotificationPermission() {
    if ('Notification' in window) {
      if (Notification.permission === 'default') {
        const permission = await Notification.requestPermission();
        return permission === 'granted';
      }
      return Notification.permission === 'granted';
    }
    return false;
  }

  // Ping périodique pour maintenir la connexion
  startPing() {
    setInterval(() => {
      if (this.isConnected) {
        this.send({
          type: 'ping',
          timestamp: new Date().toISOString()
        });
      }
    }, 30000); // Ping toutes les 30 secondes
  }
}

// Instance singleton
const alertWebSocket = new AlertWebSocket();

export default alertWebSocket;
