import React, { useState, useEffect } from 'react';
import './TicketsList.css';
import CreateTicketModal from './CreateTicketModal';
import TicketDetail from './TicketDetail';
import { PlusIcon } from './Icons';
import api from '../services/api';

const TicketsList = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    category: '',
    search: ''
  });

  useEffect(() => {
    fetchTickets();
  }, [filters]);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (filters.status) params.append('status', filters.status);
      if (filters.priority) params.append('priority', filters.priority);
      if (filters.category) params.append('category', filters.category);
      if (filters.search) params.append('search', filters.search);
      
      const response = await api.get(`/tickets/my-tickets/?${params.toString()}`);
      setTickets(response.data.results || response.data);
    } catch (err) {
      setError('Erreur lors du chargement des tickets');
      console.error('Error fetching tickets:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleTicketCreated = (newTicket) => {
    setTickets(prev => [newTicket, ...prev]);
  };

  const handleViewDetails = (ticketId) => {
    setSelectedTicket(ticketId);
  };

  const handleCloseDetails = () => {
    setSelectedTicket(null);
    // Recharger les tickets pour s'assurer que l'état est à jour
    fetchTickets();
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'open': { text: 'Ouvert', class: 'status-open' },
      'in_progress': { text: 'En cours', class: 'status-in-progress' },
      'waiting_client': { text: 'En attente', class: 'status-waiting' },
      'waiting_soc': { text: 'En attente SOC', class: 'status-waiting-soc' },
      'resolved': { text: 'Résolu', class: 'status-resolved' },
      'closed': { text: 'Fermé', class: 'status-closed' },
      'cancelled': { text: 'Annulé', class: 'status-cancelled' }
    };
    
    const config = statusConfig[status] || { text: status, class: 'status-default' };
    return <span className={`status-badge ${config.class}`}>{config.text}</span>;
  };

  const getPriorityBadge = (priority) => {
    const priorityConfig = {
      'low': { text: 'Faible', class: 'priority-low' },
      'medium': { text: 'Moyen', class: 'priority-medium' },
      'high': { text: 'Élevé', class: 'priority-high' },
      'critical': { text: 'Critique', class: 'priority-critical' }
    };
    
    const config = priorityConfig[priority] || { text: priority, class: 'priority-default' };
    return <span className={`priority-badge ${config.class}`}>{config.text}</span>;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="tickets-loading">
        <div className="loading-spinner"></div>
        <p>Chargement de vos tickets...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tickets-error">
        <h3>Erreur de chargement</h3>
        <p>{error}</p>
        <button onClick={fetchTickets} className="btn btn-primary">
          Réessayer
        </button>
      </div>
    );
  }

  return (
    <div className="tickets-container">
      <div className="tickets-header">
        <h1>Mes Tickets</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateForm(true)}
        >
          <PlusIcon size={16} color="#fff" />
          <span>Nouveau Ticket</span>
        </button>
      </div>

      {/* Filtres */}
      <div className="tickets-filters">
        <div className="filter-group">
          <label>Statut :</label>
          <select 
            value={filters.status} 
            onChange={(e) => handleFilterChange('status', e.target.value)}
          >
            <option value="">Tous</option>
            <option value="open">Ouvert</option>
            <option value="in_progress">En cours</option>
            <option value="waiting_client">En attente</option>
            <option value="resolved">Résolu</option>
            <option value="closed">Fermé</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Priorité :</label>
          <select 
            value={filters.priority} 
            onChange={(e) => handleFilterChange('priority', e.target.value)}
          >
            <option value="">Toutes</option>
            <option value="low">Faible</option>
            <option value="medium">Moyen</option>
            <option value="high">Élevé</option>
            <option value="critical">Critique</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Catégorie :</label>
          <select 
            value={filters.category} 
            onChange={(e) => handleFilterChange('category', e.target.value)}
          >
            <option value="">Toutes</option>
            <option value="support">Support technique</option>
            <option value="incident">Incident de sécurité</option>
            <option value="feature_request">Demande de fonctionnalité</option>
            <option value="account">Gestion de compte</option>
            <option value="billing">Facturation</option>
            <option value="training">Formation</option>
            <option value="consultation">Consultation</option>
            <option value="other">Autre</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Recherche :</label>
          <input
            type="text"
            placeholder="Rechercher dans les tickets..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </div>
      </div>

      {/* Liste des tickets */}
      <div className="tickets-list">
        {tickets.length === 0 ? (
          <div className="no-tickets">
            <p>Vous n'avez aucun ticket pour le moment.</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateForm(true)}
            >
              Créer votre premier ticket
            </button>
          </div>
        ) : (
          tickets.map(ticket => (
            <div key={ticket.id} className="ticket-card">
              <div className="ticket-header">
                <div className="ticket-id">
                  <strong>{ticket.ticket_id}</strong>
                </div>
                <div className="ticket-badges">
                  {getStatusBadge(ticket.status)}
                  {getPriorityBadge(ticket.priority)}
                </div>
              </div>
              
              <div className="ticket-content">
                <h3 className="ticket-title">{ticket.title}</h3>
                <p className="ticket-description">
                  {ticket.description.length > 150 
                    ? `${ticket.description.substring(0, 150)}...` 
                    : ticket.description
                  }
                </p>
              </div>
              
              <div className="ticket-meta">
                <div className="ticket-info">
                  <span className="ticket-category">{ticket.category_display}</span>
                  <span className="ticket-date">Créé le {formatDate(ticket.created_at)}</span>
                </div>
                <div className="ticket-actions">
                  <button 
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleViewDetails(ticket.ticket_id)}
                  >
                    Voir détails
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Formulaire de création */}
      <CreateTicketModal
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onTicketCreated={handleTicketCreated}
      />

      {/* Page de détails du ticket */}
      {selectedTicket && (
        <TicketDetail
          ticketId={selectedTicket}
          onClose={handleCloseDetails}
        />
      )}
    </div>
  );
};

export default TicketsList;
