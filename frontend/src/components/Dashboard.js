import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import api from '../services/api';
import alertWebSocket from '../services/websocket';
import StatsCards from './dashboard/StatsCards';
import RiskScoreChart from './dashboard/RiskScoreChart';
import RecentAlerts from './dashboard/RecentAlerts';
import { FiRefreshCw, FiTrendingUp, FiShield, FiActivity } from 'react-icons/fi';

const Dashboard = () => {
  const [alertStats, setAlertStats] = useState({
    total_alerts: 0,
    open_alerts: 0,
    closed_alerts: 0,
    avg_risk_score: 0
  });
  const [riskStats, setRiskStats] = useState({
    overall: {},
    risk_levels: {},
    time_based: {},
    top_risk_factors: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [realtimeAlerts, setRealtimeAlerts] = useState([]);

  useEffect(() => {
    fetchDashboardStats();
    setupWebSocket();
    
    // Cleanup WebSocket on unmount
    return () => {
      alertWebSocket.disconnect();
    };
  }, []);

  const setupWebSocket = async () => {
    try {
      // Demander la permission pour les notifications
      await alertWebSocket.requestNotificationPermission();
      
      // Configurer les callbacks
      alertWebSocket.subscribe((type, data) => {
        if (type === 'alert') {
          handleNewAlert(data);
        } else if (type === 'integration_status') {
          handleIntegrationStatus(data);
        }
      });
      
      // Démarrer la connexion
      alertWebSocket.connect();
      setWsConnected(true);
      
      // Démarrer le ping périodique
      alertWebSocket.startPing();
      
    } catch (error) {
      console.error('❌ Erreur configuration WebSocket:', error);
    }
  };

  const handleNewAlert = (alertData) => {
    console.log('🚨 Nouvelle alerte reçue en temps réel:', alertData);
    
    // Ajouter à la liste des alertes temps réel
    setRealtimeAlerts(prev => [alertData, ...prev.slice(0, 9)]); // Garder les 10 dernières
    
    // Rafraîchir les statistiques
    fetchDashboardStats();
  };

  const handleIntegrationStatus = (statusData) => {
    console.log('📊 Mise à jour statut intégration:', statusData);
    // Optionnel: afficher une notification de statut
  };

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      setRefreshing(true);
      console.log('Fetching dashboard stats...');
      
      // Fetch alert statistics
      const alertResponse = await api.get('/alerts/statistics/');
      console.log('Alert stats response:', alertResponse.data);
      setAlertStats(alertResponse.data);
      
      // Fetch risk score statistics
      const riskResponse = await api.get('/analytics/risk-score-statistics/');
      console.log('Risk stats response:', riskResponse.data);
      setRiskStats(riskResponse.data);
      
    } catch (err) {
      console.error('Dashboard stats error:', err);
      setError('Erreur de chargement des statistiques du tableau de bord');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <h3>Chargement du tableau de bord</h3>
          <p>Récupération des données de sécurité...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <div className="error-container">
          <FiShield className="error-icon" />
          <h3>Erreur de chargement</h3>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchDashboardStats}>
            <FiRefreshCw className="btn-icon" />
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Tableau de bord de sécurité EXEO</h1>
        <div className="dashboard-actions">
          <div className="connection-status">
            <div className={`status-indicator ${wsConnected ? 'connected' : 'disconnected'}`}>
              <div className="status-dot"></div>
              <span>{wsConnected ? 'Temps réel actif' : 'Hors ligne'}</span>
            </div>
          </div>
          <button 
            className={`btn btn-primary ${refreshing ? 'refreshing' : ''}`} 
            onClick={fetchDashboardStats}
            disabled={refreshing}
          >
            <FiRefreshCw className={`btn-icon ${refreshing ? 'spinning' : ''}`} />
            {refreshing ? 'Actualisation...' : 'Actualiser'}
          </button>
        </div>
      </div>

      {/* Métriques principales */}
      <StatsCards statistics={alertStats} />

      {/* Graphiques et analyses */}
      <div className="charts-grid">
        <div className="chart-container">
          <RiskScoreChart />
        </div>
        
        <div className="chart-container">
          <RecentAlerts />
        </div>
      </div>

      {/* Informations de scoring */}
      {riskStats.overall && (
        <div className="dashboard-info">
          <div className="info-card">
            <h3>Score de risque moyen</h3>
            <p className="info-value">{riskStats.overall.avg_risk_score?.toFixed(2) || '0.00'}/10</p>
          </div>
          
          <div className="info-card">
            <h3>Score maximum</h3>
            <p className="info-value">{riskStats.overall.max_risk_score?.toFixed(2) || '0.00'}/10</p>
          </div>
          
          <div className="info-card">
            <h3>Alertes critiques (8+)</h3>
            <p className="info-value">{riskStats.risk_levels?.critical || 0}</p>
          </div>
          
          <div className="info-card">
            <h3>Alertes haute priorité (6+)</h3>
            <p className="info-value">{riskStats.risk_levels?.high || 0}</p>
          </div>
        </div>
      )}

      {/* Facteurs de risque principaux */}
      {riskStats.top_risk_factors && riskStats.top_risk_factors.length > 0 && (
        <div className="risk-factors-section">
          <h3>Facteurs de risque principaux</h3>
          <div className="risk-factors-grid">
            {riskStats.top_risk_factors.slice(0, 5).map((factor, index) => (
              <div key={index} className="risk-factor-item">
                <span className="risk-factor-name">{factor[0]}</span>
                <span className="risk-factor-count">{factor[1]} occurrences</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};


export default Dashboard;
