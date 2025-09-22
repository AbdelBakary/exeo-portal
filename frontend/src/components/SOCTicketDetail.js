import React, { useState, useEffect } from 'react';
import './SOCTicketDetail.css';
import { SecurityIcon, UserIcon } from './Icons';
import api from '../services/api';

const SOCTicketDetail = ({ ticketId, onClose }) => {
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
      const response = await api.get(`/tickets/ticket/${ticketId}/`);
      setTicket(response.data);
    } catch (err) {
      setError('Erreur lors du chargement du ticket');
      console.error('Error fetching ticket:', err);
    }
  };

  const fetchComments = async () => {
    try {
      const response = await api.get(`/tickets/ticket/${ticketId}/comments/`);
      const commentsData = response.data.results || response.data;
      setComments(Array.isArray(commentsData) ? commentsData : []);
    } catch (err) {
      console.error('Error fetching comments:', err);
      setComments([]);
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
        comment_type: 'soc'
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

  const handleUpdateStatus = async (newStatus) => {
    try {
      await api.patch(`/tickets/ticket/${ticketId}/`, {
        status: newStatus
      });
      setTicket(prev => ({ ...prev, status: newStatus }));
    } catch (err) {
      setError('Erreur lors de la mise à jour du statut');
      console.error('Error updating status:', err);
    }
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
      <div className="soc-ticket-detail-loading">
        <div className="loading-spinner"></div>
        <p>Chargement des détails du ticket...</p>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div className="soc-ticket-detail-error">
        <h3>Erreur de chargement</h3>
        <p>{error || 'Ticket non trouvé'}</p>
        <button onClick={onClose} className="btn btn-primary">
          Retour
        </button>
      </div>
    );
  }

  return (
    <div className="soc-ticket-detail-overlay">
      <div className="soc-ticket-detail-container">
        <div className="soc-ticket-detail-header">
          <div className="soc-ticket-detail-title">
            <h1>
              <SecurityIcon size={24} color="#1A3D6D" />
              <span>{ticket.ticket_id}</span>
            </h1>
            <div className="ticket-badges">
              {getStatusBadge(ticket.status)}
              {getPriorityBadge(ticket.priority)}
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="soc-ticket-detail-content">
          <div className="ticket-info">
            <h2>{ticket.title}</h2>
            <div className="ticket-meta">
              <div className="meta-item">
                <strong>Client:</strong> {ticket.client_name}
              </div>
              <div className="meta-item">
                <strong>Créé par:</strong> {ticket.created_by_name}
              </div>
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
                      {comment.comment_type === 'client' ? 
                        <UserIcon size={16} color="#666" /> : 
                        <SecurityIcon size={16} color="#1A3D6D" />
                      }
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

            <div className="add-comment-section">
              <h4>✍️ Répondre au client</h4>
              <form onSubmit={handleAddComment} className="add-comment-form">
                <div className="form-group">
                  <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Tapez votre réponse ici..."
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
                        📤 Envoyer la réponse
                      </>
                    )}
                  </button>
                  <small className="comment-hint">
                    Votre réponse sera visible par le client
                  </small>
                </div>
              </form>
            </div>

            <div className="ticket-actions">
              <h4>🔧 Actions sur le ticket</h4>
              <div className="action-buttons">
                {ticket.status === 'open' && (
                  <button 
                    onClick={() => handleUpdateStatus('in_progress')}
                    className="btn btn-warning"
                  >
                    🔄 Marquer en cours
                  </button>
                )}
                {ticket.status === 'in_progress' && (
                  <button 
                    onClick={() => handleUpdateStatus('waiting_client')}
                    className="btn btn-info"
                  >
                    ⏳ En attente client
                  </button>
                )}
                {ticket.status !== 'resolved' && ticket.status !== 'closed' && (
                  <button 
                    onClick={() => handleUpdateStatus('resolved')}
                    className="btn btn-success"
                  >
                    <SecurityIcon size={16} color="#28a745" /> Marquer résolu
                  </button>
                )}
                {ticket.status === 'resolved' && (
                  <button 
                    onClick={() => handleUpdateStatus('closed')}
                    className="btn btn-secondary"
                  >
                    <SecurityIcon size={16} color="#6c757d" /> Fermer le ticket
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SOCTicketDetail;
