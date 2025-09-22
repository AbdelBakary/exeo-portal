import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import Logo from './Logo';
import './Login.css';
import api from '../services/api';

const Login = () => {
  const { loginWithToken } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/login/', formData);
      const data = response.data;
      
      // Utiliser la fonction loginWithToken du hook useAuth
      await loginWithToken(data.token, data.user);
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Erreur de connexion au serveur');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <Logo size="large" variant="simple" />
          <h2>Connexion</h2>
          <p>Accédez à votre portail de cybersécurité</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="votre@email.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Mot de passe</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Votre mot de passe"
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
          
          <p className="signature-inline">Made by <strong>Imane Bakary</strong> for <strong>EXEO</strong></p>
        </form>

        <div className="login-footer">
          <div className="demo-accounts">
            <h4>Comptes de démonstration</h4>
            <div className="demo-account">
              <div className="account-type">Administrateur</div>
              <div className="account-credentials">admin@exeo.com / admin123</div>
            </div>
            <div className="demo-account">
              <div className="account-type">Analyste SOC</div>
              <div className="account-credentials">analyst@exeo.com / analyst123</div>
            </div>
            <div className="demo-account">
              <div className="account-type">Client</div>
              <div className="account-credentials">test@example.com / testpass123</div>
            </div>
          </div>
          <p className="footer-text">Portail de cybersécurité multi-tenant</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
