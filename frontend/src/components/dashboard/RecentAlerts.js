import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { alertService } from '../../services/alertService';
import { FiAlertTriangle, FiClock, FiUser, FiArrowRight, FiShield } from 'react-icons/fi';

const RecentAlerts = () => {
  const { data: alerts, isLoading } = useQuery(
    'recentAlerts',
    () => alertService.getAlerts({ limit: 10, ordering: '-detected_at' }),
    {
      refetchInterval: 30000,
    }
  );

  const getSeverityColor = (severity) => {
    const colors = {
      low: 'text-green-700 bg-green-100 border-green-200',
      medium: 'text-yellow-700 bg-yellow-100 border-yellow-200',
      high: 'text-orange-700 bg-orange-100 border-orange-200',
      critical: 'text-red-700 bg-red-100 border-red-200',
    };
    return colors[severity] || 'text-gray-700 bg-gray-100 border-gray-200';
  };

  const getSeverityLabel = (severity) => {
    const labels = {
      low: 'Faible',
      medium: 'Moyen',
      high: 'Élevé',
      critical: 'Critique',
    };
    return labels[severity] || severity;
  };

  const getStatusColor = (status) => {
    const colors = {
      open: 'text-red-700 bg-red-100 border-red-200',
      in_progress: 'text-yellow-700 bg-yellow-100 border-yellow-200',
      closed: 'text-green-700 bg-green-100 border-green-200',
      false_positive: 'text-gray-700 bg-gray-100 border-gray-200',
    };
    return colors[status] || 'text-gray-700 bg-gray-100 border-gray-200';
  };

  const getStatusLabel = (status) => {
    const labels = {
      open: 'Ouvert',
      in_progress: 'En cours',
      closed: 'Fermé',
      false_positive: 'Faux positif',
    };
    return labels[status] || status;
  };

  const getRiskScoreColor = (score) => {
    if (score >= 8) return 'text-red-600';
    if (score >= 6) return 'text-orange-600';
    if (score >= 4) return 'text-yellow-600';
    return 'text-green-600';
  };

  if (isLoading) {
    return (
      <div className="recent-alerts-card">
        <div className="recent-alerts-header">
          <h3>Alertes récentes</h3>
        </div>
        <div className="recent-alerts-body">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Chargement des alertes...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="recent-alerts-card">
      <div className="recent-alerts-header">
        <div className="header-content">
          <h3>Alertes récentes</h3>
          <div className="header-badge">
            <FiShield className="w-4 h-4" />
            <span>{alerts?.results?.length || 0}</span>
          </div>
        </div>
        <Link to="/alerts" className="view-all-link">
          Voir toutes
          <FiArrowRight className="w-4 h-4" />
        </Link>
      </div>
      
      <div className="recent-alerts-body">
        {alerts?.results?.length > 0 ? (
          <div className="alerts-list">
            {alerts.results.map((alert, index) => (
              <div key={alert.id} className="alert-item">
                <div className="alert-main">
                  <div className="alert-icon">
                    <FiAlertTriangle className="w-4 h-4" />
                  </div>
                  <div className="alert-content">
                    <div className="alert-title">{alert.title}</div>
                    <div className="alert-description">{alert.description}</div>
                    <div className="alert-meta">
                      <div className="meta-item">
                        <FiClock className="w-3 h-3" />
                        {new Date(alert.detected_at).toLocaleDateString('fr-FR')}
                      </div>
                      {alert.assigned_to_name && (
                        <div className="meta-item">
                          <FiUser className="w-3 h-3" />
                          {alert.assigned_to_name}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="alert-sidebar">
                  <div className="alert-badges">
                    <span className={`severity-badge ${getSeverityColor(alert.severity)}`}>
                      {getSeverityLabel(alert.severity)}
                    </span>
                    <span className={`status-badge ${getStatusColor(alert.status)}`}>
                      {getStatusLabel(alert.status)}
                    </span>
                  </div>
                  <div className={`risk-score ${getRiskScoreColor(alert.risk_score)}`}>
                    Score: {alert.risk_score?.toFixed(1) || 'N/A'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <FiAlertTriangle className="empty-icon" />
            <h4>Aucune alerte récente</h4>
            <p>Toutes les alertes ont été traitées</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentAlerts;
