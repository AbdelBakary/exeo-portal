import React, { useState, useEffect } from 'react';
import './IncidentsList.css';
import api from '../services/api';

const IncidentsList = () => {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    priority: '',
    status: '',
    category: '',
    min_impact_score: '',
    max_impact_score: ''
  });
  const [sortBy, setSortBy] = useState('reported_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchIncidents();
  }, [filters, sortBy, sortOrder, currentPage]);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        page: currentPage,
        ordering: sortOrder === 'desc' ? `-${sortBy}` : sortBy,
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''))
      };
      
      const response = await api.get('/incidents/', { params });
      console.log('Incidents response:', response.data); // Debug
      
      // Protection contre les données invalides
      const incidentsData = response.data?.results || response.data || [];
      setIncidents(Array.isArray(incidentsData) ? incidentsData : []);
      setTotalPages(response.data?.total_pages || 1);
    } catch (err) {
      console.error('Error fetching incidents:', err); // Debug
      setError(err.response?.data?.detail || err.message || 'Erreur de chargement');
      setIncidents([]); // S'assurer que incidents est un tableau vide en cas d'erreur
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
      priority: '',
      status: '',
      category: '',
      min_impact_score: '',
      max_impact_score: ''
    });
    setCurrentPage(1);
  };

  if (loading) {
    return (
      <div className="incidents-loading">
        <div className="loading-spinner"></div>
        <p>Chargement des incidents...</p>
      </div>
    );
  }

  return (
    <div className="incidents-list">
      <div className="incidents-header">
        <h1>Incidents de sécurité</h1>
        <div className="incidents-actions">
          <button className="btn btn-primary" onClick={fetchIncidents}>
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
              placeholder="Rechercher dans les incidents..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
            />
          </div>
          
          <div className="filter-group">
            <label>Priorité</label>
            <select
              value={filters.priority}
              onChange={(e) => handleFilterChange('priority', e.target.value)}
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
              <option value="new">Nouveau</option>
              <option value="assigned">Assigné</option>
              <option value="in_progress">En cours</option>
              <option value="on_hold">En attente</option>
              <option value="resolved">Résolu</option>
              <option value="closed">Fermé</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>Catégorie</label>
            <select
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
            >
              <option value="">Toutes</option>
              <option value="malware">Malware</option>
              <option value="phishing">Phishing</option>
              <option value="ddos">DDoS</option>
              <option value="data_breach">Fuite de données</option>
              <option value="insider_threat">Menace interne</option>
              <option value="vulnerability">Vulnérabilité</option>
              <option value="policy_violation">Violation de politique</option>
              <option value="other">Autre</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>Score d'impact min</label>
            <input
              type="number"
              min="0"
              max="10"
              step="0.1"
              placeholder="0"
              value={filters.min_impact_score}
              onChange={(e) => handleFilterChange('min_impact_score', e.target.value)}
            />
          </div>
          
          <div className="filter-group">
            <label>Score d'impact max</label>
            <input
              type="number"
              min="0"
              max="10"
              step="0.1"
              placeholder="10"
              value={filters.max_impact_score}
              onChange={(e) => handleFilterChange('max_impact_score', e.target.value)}
            />
          </div>
        </div>
        
        <div className="filters-actions">
          <button className="btn btn-secondary" onClick={clearFilters}>
            Effacer les filtres
          </button>
        </div>
      </div>

      {/* Tableau des incidents */}
      <div className="incidents-table-container">
        <table className="incidents-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('incident_id')} className="sortable">
                ID {sortBy === 'incident_id' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('title')} className="sortable">
                Titre {sortBy === 'title' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('priority')} className="sortable">
                Priorité {sortBy === 'priority' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('status')} className="sortable">
                Statut {sortBy === 'status' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('impact_score')} className="sortable">
                Score d'impact {sortBy === 'impact_score' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('reported_at')} className="sortable">
                Signalé le {sortBy === 'reported_at' && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {incidents && incidents.length > 0 ? (
              incidents.map((incident) => (
                <IncidentRow key={incident.id} incident={incident} />
              ))
            ) : (
              <tr>
                <td colSpan="7" className="no-data">
                  Aucun incident trouvé
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
        <div className="incidents-error">
          <h3>Erreur de chargement</h3>
          <p>{error}</p>
          <button onClick={fetchIncidents}>Réessayer</button>
        </div>
      )}
    </div>
  );
};

const IncidentRow = ({ incident }) => {
  const [expanded, setExpanded] = useState(false);

  const getPriorityColor = (priority) => {
    const colors = {
      'low': '#28a745',
      'medium': '#ffc107',
      'high': '#fd7e14',
      'critical': '#dc3545'
    };
    return colors[priority] || '#6c757d';
  };

  const getStatusColor = (status) => {
    const colors = {
      'new': '#dc3545',
      'assigned': '#ffc107',
      'in_progress': '#17a2b8',
      'on_hold': '#6c757d',
      'resolved': '#28a745',
      'closed': '#6c757d'
    };
    return colors[status] || '#6c757d';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('fr-FR');
  };

  return (
    <>
      <tr className="incident-row" onClick={() => setExpanded(!expanded)}>
        <td className="incident-id">{incident.incident_id}</td>
        <td className="incident-title">{incident.title}</td>
        <td>
          <span 
            className="priority-badge"
            style={{ backgroundColor: getPriorityColor(incident.priority) }}
          >
            {incident.priority_display}
          </span>
        </td>
        <td>
          <span 
            className="status-badge"
            style={{ backgroundColor: getStatusColor(incident.status) }}
          >
            {incident.status_display}
          </span>
        </td>
        <td className="impact-score">
          <div className="impact-score-container">
            <div 
              className="impact-score-bar"
              style={{ 
                width: `${(incident.impact_score / 10) * 100}%`,
                backgroundColor: incident.impact_score > 7 ? '#dc3545' : 
                               incident.impact_score > 4 ? '#ffc107' : '#28a745'
              }}
            ></div>
            <span className="impact-score-value">{incident.impact_score.toFixed(1)}</span>
          </div>
        </td>
        <td className="incident-date">{formatDate(incident.reported_at)}</td>
        <td className="incident-actions">
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
        <tr className="incident-details">
          <td colSpan="7">
            <div className="incident-details-content">
              <div className="incident-description">
                <h4>Description</h4>
                <p>{incident.description}</p>
              </div>
              
              <div className="incident-metadata">
                <div className="metadata-item">
                  <strong>Catégorie:</strong> {incident.category_display}
                </div>
                <div className="metadata-item">
                  <strong>Client:</strong> {incident.client_name}
                </div>
                <div className="metadata-item">
                  <strong>Assigné à:</strong> {incident.assigned_to_name || 'Non assigné'}
                </div>
                <div className="metadata-item">
                  <strong>Utilisateurs affectés:</strong> {incident.affected_users}
                </div>
              </div>
              
              <div className="incident-actions-detailed">
                <button className="btn btn-sm btn-primary">Assigner</button>
                <button className="btn btn-sm btn-secondary">Commenter</button>
                <button className="btn btn-sm btn-warning">Modifier le statut</button>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
};

export default IncidentsList;
