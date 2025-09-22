import React, { useState, useEffect } from 'react';
import './TicketDetail.css';
import api from '../services/api';

const TicketDetail = ({ ticketId, onClose }) => {
  const [ticket, setTicket] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (ticketId) {
      fetchTicketDetails();
      fetchComments();
    }
  }, [ticketId]);

  const fetchTicketDetails = async () => {
    try {
      setError(null);
      const response = await api.get(`/tickets/ticket/${ticketId}/`);
      setTicket(response.data);
    } catch (err) {
      console.error('Error fetching ticket:', err);
      if (err.response?.status === 403) {
        setError('Vous n\'avez pas la permission de voir ce ticket');
      } else if (err.response?.status === 404) {
        setError('Ticket non trouvé');
      } else {
        setError('Erreur lors du chargement du ticket');
      }
    }
  };

  const fetchComments = async () => {
    try {
      const response = await api.get(`/tickets/ticket/${ticketId}/comments/`);
      // L'API retourne un objet avec pagination, les commentaires sont dans 'results'
      const commentsData = response.data.results || response.data;
      setComments(Array.isArray(commentsData) ? commentsData : []);
    } catch (err) {
      console.error('Error fetching comments:', err);
      setComments([]); // Initialiser avec un tableau vide en cas d'erreur
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setSubmittingComment(true);
    try {
      const response = await api.post(`/tickets/ticket/${ticketId}/comments/`, {
        content: newComment,
        comment_type: 'client'
      });
      setComments(prev => [...prev, response.data]);
      setNewComment('');
    } catch (err) {
      setError('Erreur lors de l\'ajout du commentaire');
      console.error('Error adding comment:', err);
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleCloseTicket = async () => {
    if (!window.confirm('Êtes-vous sûr de vouloir fermer ce ticket ? Cette action est irréversible.')) {
      return;
    }

    try {
      await api.patch(`/tickets/ticket/${ticketId}/`, {
        status: 'resolved'
      });
      setTicket(prev => ({ ...prev, status: 'resolved' }));
      // Ajouter un commentaire système
      await api.post(`/tickets/ticket/${ticketId}/comments/`, {
        content: 'Ticket fermé par le client - Problème résolu',
        comment_type: 'system'
      });
      // Recharger les commentaires
      fetchComments();
    } catch (err) {
      setError('Erreur lors de la fermeture du ticket');
      console.error('Error closing ticket:', err);
    }
  };

  // Gérer la fermeture avec Escape
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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

  if (loading) {
    return (
      <div className="ticket-detail-loading">
        <div className="loading-spinner"></div>
        <p>Chargement des détails du ticket...</p>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div className="ticket-detail-overlay">
        <div className="ticket-detail-container">
          <div className="ticket-detail-error">
            <h3>Erreur de chargement</h3>
            <p>{error || 'Ticket non trouvé'}</p>
            <div className="error-actions">
              <button onClick={fetchTicketDetails} className="btn btn-primary">
                🔄 Réessayer
              </button>
              <button onClick={onClose} className="btn btn-secondary">
                Retour
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ticket-detail-overlay" onClick={(e) => {
      if (e.target === e.currentTarget) {
        onClose();
      }
    }}>
      <div className="ticket-detail-container">
        <div className="ticket-detail-header">
          <div className="ticket-detail-title">
            <h1>
              <span className="ticket-icon">🎫</span>
              <span>{ticket.ticket_id}</span>
            </h1>
            <div className="ticket-badges">
              {getStatusBadge(ticket.status)}
              {getPriorityBadge(ticket.priority)}
            </div>
          </div>
          <button className="close-btn" onClick={onClose} title="Fermer">×</button>
        </div>

        <div className="ticket-detail-content">
          <div className="ticket-info">
            <h2>{ticket.title}</h2>
            <div className="ticket-meta">
              <div className="meta-item">
                <strong>Catégorie:</strong> {ticket.category_display}
              </div>
              <div className="meta-item">
                <strong>Créé le:</strong> {formatDate(ticket.created_at)}
              </div>
              <div className="meta-item">
                <strong>Dernière mise à jour:</strong> {formatDate(ticket.updated_at)}
              </div>
              {ticket.assigned_to_name && (
                <div className="meta-item">
                  <strong>Assigné à:</strong> {ticket.assigned_to_name}
                </div>
              )}
            </div>
            <div className="ticket-description">
              <h3>Description</h3>
              <p>{ticket.description}</p>
            </div>
          </div>

          <div className="ticket-conversation">
            <div className="conversation-header">
              <h3>💬 Conversation</h3>
              <div className="conversation-stats">
                {Array.isArray(comments) && comments.length > 0 && (
                  <span className="comment-count">{comments.length} message{comments.length > 1 ? 's' : ''}</span>
                )}
              </div>
            </div>
            
            <div className="comments-timeline">
              {Array.isArray(comments) && comments.length > 0 ? (
                comments.map((comment, index) => (
                  <div key={comment.id} className={`comment-item ${comment.comment_type}`}>
                    <div className="comment-avatar">
                      {comment.comment_type === 'client' ? '👤' : '🛡️'}
                    </div>
                    <div className="comment-content-wrapper">
                      <div className="comment-header">
                        <div className="comment-author">
                          <strong>{comment.author_name}</strong>
                          <span className={`comment-role ${comment.comment_type}`}>
                            {comment.comment_type === 'client' ? 'Client' : 'SOC Analyst'}
                          </span>
                        </div>
                        <span className="comment-date">{formatDate(comment.created_at)}</span>
                      </div>
                      <div className="comment-message">
                        {comment.content}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-comments">
                  <div className="no-comments-icon">💬</div>
                  <p>Aucun message dans cette conversation</p>
                  <small>Commencez la conversation en ajoutant un commentaire ci-dessous</small>
                </div>
              )}
            </div>

            {ticket.status === 'resolved' || ticket.status === 'closed' ? (
              <div className="ticket-closed-section">
                <div className="closed-message">
                  <h4>🛡️ Ticket fermé</h4>
                  <p>Ce ticket a été fermé. La conversation n'est plus active.</p>
                  {ticket.status === 'resolved' && (
                    <p className="resolved-info">
                      ✅ <strong>Résolu</strong> - Le problème a été résolu
                    </p>
                  )}
                  {ticket.status === 'closed' && (
                    <p className="closed-info">
                      🔒 <strong>Fermé</strong> - Le ticket a été fermé définitivement
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <div className="add-comment-section">
                <h4>✍️ Ajouter un message</h4>
                <form onSubmit={handleAddComment} className="add-comment-form">
                  <div className="form-group">
                    <textarea
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      placeholder="Tapez votre message ici..."
                      rows="4"
                      required
                      className="comment-textarea"
                    />
                  </div>
                  <div className="form-actions">
                    <button 
                      type="submit" 
                      className="btn btn-primary btn-send"
                      disabled={submittingComment || !newComment.trim()}
                    >
                      {submittingComment ? (
                        <>
                          <span className="spinner"></span>
                          Envoi en cours...
                        </>
                      ) : (
                        <>
                          📤 Envoyer le message
                        </>
                      )}
                    </button>
                    <small className="comment-hint">
                      Votre message sera visible par l'équipe SOC
                    </small>
                  </div>
                </form>
                
                <div className="ticket-actions">
                  <h5>🔧 Actions sur le ticket</h5>
                  <button 
                    onClick={handleCloseTicket}
                    className="btn btn-success btn-close-ticket"
                  >
                    ✅ Fermer le ticket (Problème résolu)
                  </button>
                  <small className="close-hint">
                    Fermez le ticket si votre problème est résolu
                  </small>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TicketDetail;
