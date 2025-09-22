import React, { useState, useEffect } from 'react';
import './AlertsList.css';
import api from '../services/api';

const AlertsList = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    severity: '',
    status: '',
    alert_type: '',
    min_risk_score: '',
    max_risk_score: ''
  });
  const [sortBy, setSortBy] = useState('detected_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchAlerts();
  }, [filters, sortBy, sortOrder, currentPage]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        ordering: sortOrder === 'desc' ? `-${sortBy}` : sortBy,
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''))
      };
      
      const response = await api.get('/alerts/', { params });
      setAlerts(response.data.results || response.data);
      setTotalPages(response.data.total_pages || 1);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      severity: '',
      status: '',
      alert_type: '',
      min_risk_score: '',
      max_risk_score: ''
    });
    setCurrentPage(1);
  };

  if (loading) {
    return (
      <div className="alerts-loading">
        <div className="loading-spinner"></div>
        <p>Chargement des alertes...</p>
      </div>
    );
  }

  return (
    <div className="alerts-list">
      <div className="alerts-header">
        <h1>Alertes de sécurité</h1>
        <div className="alerts-actions">
          <button className="btn btn-primary" onClick={fetchAlerts}>
            Actualiser
          </button>
        </div>
      </div>

      {/* Filtres */}
      <div className="filters-section">
        <div className="filters-grid">
          <div className="filter-group">
            <label>Recherche</label>
            <input
              type="text"
              placeholder="Rechercher dans les alertes..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
            />
          </div>
          
          <div className="filter-group">
            <label>Sévérité</label>
            <select
              value={filters.severity}
              onChange={(e) => handleFilterChange('severity', e.target.value)}
            >
              <option value="">Toutes</option>
              <option value="low">Faible</option>
              <option value="medium">Moyenne</option>
              <option value="high">Élevée</option>
              <option value="critical">Critique</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>Statut</label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <option value="">Tous</option>
              <option value="open">Ouvert</option>
              <option value="in_progress">En cours</option>
              <option value="closed">Fermé</option>
              <option value="false_positive">Faux positif</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>Type d'alerte</label>
            <select
              value={filters.alert_type}
              onChange={(e) => handleFilterChange('alert_type', e.target.value)}
            >
              <option value="">Tous</option>
              <option value="malware">Malware</option>
              <option value="phishing">Phishing</option>
              <option value="ddos">DDoS</option>
              <option value="intrusion">Intrusion</option>
              <option value="vulnerability">Vulnérabilité</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>Score de risque min</label>
            <input
              type="number"
              min="0"
              max="10"
              step="0.1"
              placeholder="0"
              value={filters.min_risk_score}
              onChange={(e) => handleFilterChange('min_risk_score', e.target.value)}
            />
          </div>
          
          <div className="filter-group">
            <label>Score de risque max</label>
            <input
              type="number"
              min="0"
              max="10"
              step="0.1"
              placeholder="10"
              value={filters.max_risk_score}
              onChange={(e) => handleFilterChange('max_risk_score', e.target.value)}
            />
          </div>
        </div>
        
        <div className="filters-actions">
          <button className="btn btn-secondary" onClick={clearFilters}>
            Effacer les filtres
          </button>
        </div>
      </div>

      {/* Tableau des alertes */}
      <div className="alerts-table-container">
        <table className="alerts-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('alert_id')} className="sortable">
                ID {sortBy === 'alert_id' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('title')} className="sortable">
                Titre {sortBy === 'title' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('severity')} className="sortable">
                Sévérité {sortBy === 'severity' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('status')} className="sortable">
                Statut {sortBy === 'status' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('risk_score')} className="sortable">
                Score de risque {sortBy === 'risk_score' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('detected_at')} className="sortable">
                Détecté le {sortBy === 'detected_at' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {alerts && alerts.length > 0 ? (
              alerts.map((alert) => (
                <AlertRow key={alert.id} alert={alert} />
              ))
            ) : (
              <tr>
                <td colSpan="7" className="no-data">
                  Aucune alerte trouvée
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="btn btn-secondary"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            Précédent
          </button>
          
          <span className="pagination-info">
            Page {currentPage} sur {totalPages}
          </span>
          
          <button
            className="btn btn-secondary"
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Suivant
          </button>
        </div>
      )}

      {error && (
        <div className="alerts-error">
          <h3>Erreur de chargement</h3>
          <p>{error}</p>
          <button onClick={fetchAlerts}>Réessayer</button>
        </div>
      )}
    </div>
  );
};

const AlertRow = ({ alert }) => {
  const [expanded, setExpanded] = useState(false);

  const getSeverityColor = (severity) => {
    const colors = {
      'low': '#28a745',
      'medium': '#ffc107',
      'high': '#fd7e14',
      'critical': '#dc3545'
    };
    return colors[severity] || '#6c757d';
  };

  const getStatusColor = (status) => {
    const colors = {
      'open': '#dc3545',
      'in_progress': '#17a2b8',
      'closed': '#28a745',
      'false_positive': '#6c757d'
    };
    return colors[status] || '#6c757d';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('fr-FR');
  };

  return (
    <>
      <tr className="alert-row" onClick={() => setExpanded(!expanded)}>
        <td className="alert-id">{alert.alert_id}</td>
        <td className="alert-title">{alert.title}</td>
        <td>
          <span 
            className="severity-badge"
            style={{ backgroundColor: getSeverityColor(alert.severity) }}
          >
            {alert.severity_display}
          </span>
        </td>
        <td>
          <span 
            className="status-badge"
            style={{ backgroundColor: getStatusColor(alert.status) }}
          >
            {alert.status_display}
          </span>
        </td>
        <td className="risk-score">
          <div className="risk-score-container">
            <div 
              className="risk-score-bar"
              style={{ 
                width: `${(alert.risk_score / 10) * 100}%`,
                backgroundColor: alert.risk_score > 7 ? '#dc3545' : 
                               alert.risk_score > 4 ? '#ffc107' : '#28a745'
              }}
            ></div>
            <span className="risk-score-value">{alert.risk_score.toFixed(1)}</span>
          </div>
        </td>
        <td className="alert-date">{formatDate(alert.detected_at)}</td>
        <td className="alert-actions">
          <button 
            className="btn btn-sm btn-primary"
            onClick={(e) => {
              e.stopPropagation();
              // Handle view details
            }}
          >
            Voir
          </button>
        </td>
      </tr>
      
      {expanded && (
        <tr className="alert-details">
          <td colSpan="7">
            <div className="alert-details-content">
              <div className="alert-description">
                <h4>Description</h4>
                <p>{alert.description}</p>
              </div>
              
              <div className="alert-metadata">
                <div className="metadata-item">
                  <strong>Type:</strong> {alert.alert_type_display}
                </div>
                <div className="metadata-item">
                  <strong>Source IP:</strong> {alert.source_ip || 'N/A'}
                </div>
                <div className="metadata-item">
                  <strong>Destination IP:</strong> {alert.destination_ip || 'N/A'}
                </div>
                <div className="metadata-item">
                  <strong>Analyste EXEO:</strong> {alert.assigned_to_name || 'En attente d\'assignation'}
                </div>
              </div>
              
              <div className="alert-actions-detailed">
                <div className="client-info-section">
                  <div className="info-item">
                    <strong>🔍 Détecté par:</strong> EXEO Security
                  </div>
                  <div className="info-item">
                    <strong>⏱️ Temps de résolution:</strong> {alert.resolution_time ? `${alert.resolution_time} minutes` : 'En cours...'}
                  </div>
                  <div className="info-item">
                    <strong>🛡️ Protection:</strong> {alert.status === 'closed' ? '✅ Sécurisé par EXEO' : '🔄 En cours de traitement'}
                  </div>
                </div>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
};

export default AlertsList;
