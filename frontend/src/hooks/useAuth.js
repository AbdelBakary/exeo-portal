import { useState, useEffect, createContext, useContext } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fonction pour vérifier si le token est valide
  const isTokenValid = (token) => {
    if (!token) return false;
    try {
      // Décoder le token JWT pour vérifier l'expiration
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp > currentTime;
    } catch (error) {
      return false;
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        
        if (token) {
          // Essayer de récupérer les données utilisateur avec le token
          try {
            const userData = await authService.getProfile();
            setUser(userData);
          } catch (profileError) {
            // Si l'erreur est 401, le token est invalide côté serveur
            if (profileError.response?.status === 401) {
              localStorage.removeItem('token');
              setUser(null);
            }
            // Autre erreur réseau, on garde le token pour retry
          }
        }
      } catch (error) {
        localStorage.removeItem('token');
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authService.login(email, password);
      const { token, user: userData } = response;
      
      localStorage.setItem('token', token);
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Erreur de connexion' 
      };
    }
  };

  const loginWithToken = async (token, userData) => {
    try {
      localStorage.setItem('token', token);
      setUser(userData);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: 'Erreur de connexion' 
      };
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      setUser(null);
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const updatedUser = await authService.updateProfile(profileData);
      setUser(updatedUser);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Erreur de mise à jour' 
      };
    }
  };

  const changePassword = async (oldPassword, newPassword) => {
    try {
      await authService.changePassword(oldPassword, newPassword);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Erreur de changement de mot de passe' 
      };
    }
  };

  // Fonction pour rafraîchir le token
  const refreshToken = async () => {
    try {
      const response = await authService.refreshToken();
      const { token } = response;
      localStorage.setItem('token', token);
      return { success: true };
    } catch (error) {
      console.error('Token refresh failed:', error);
      localStorage.removeItem('token');
      setUser(null);
      return { success: false };
    }
  };

  const value = {
    user,
    loading,
    login,
    loginWithToken,
    logout,
    updateProfile,
    changePassword,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
