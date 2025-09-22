import React, { useState } from 'react';
import './CreateTicketModal.css';
import api from '../services/api';

const CreateTicketModal = ({ isOpen, onClose, onTicketCreated }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'support',
    priority: 'medium',
    tags: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/tickets/my-tickets/', formData);
      onTicketCreated(response.data);
      onClose();
      // Reset form
      setFormData({
        title: '',
        description: '',
        category: 'support',
        priority: 'medium',
        tags: []
      });
    } catch (err) {
      setError('Erreur lors de la création du ticket');
      console.error('Error creating ticket:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content create-ticket-modal">
        <div className="modal-header">
          <h2>Créer un nouveau ticket</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="ticket-form">
          <div className="form-group">
            <label htmlFor="title">Titre du ticket *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="Décrivez brièvement votre problème"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="category">Catégorie *</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                required
              >
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

            <div className="form-group">
              <label htmlFor="priority">Priorité *</label>
              <select
                id="priority"
                name="priority"
                value={formData.priority}
                onChange={handleInputChange}
                required
              >
                <option value="low">Faible</option>
                <option value="medium">Moyen</option>
                <option value="high">Élevé</option>
                <option value="critical">Critique</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description détaillée *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Décrivez votre problème en détail. Plus vous fournirez d'informations, plus nous pourrons vous aider rapidement."
              rows="6"
              required
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Annuler
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Création...' : 'Créer le ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateTicketModal;
