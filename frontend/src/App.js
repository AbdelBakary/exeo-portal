import React, { useState } from 'react';
import { AuthProvider, useAuth } from './hooks/useAuth';
import Dashboard from './components/Dashboard';
import AlertsList from './components/AlertsList';
import IncidentsList from './components/IncidentsList';
import Reports from './components/Reports';
import TicketsList from './components/TicketsList';
import SOCTicketsList from './components/SOCTicketsList';
import Login from './components/Login';
import Logo from './components/Logo';
import { 
  DashboardIcon, 
  AlertsIcon, 
  IncidentsIcon, 
  TicketsIcon, 
  ReportsIcon, 
  UserIcon, 
  LogoutIcon 
} from './components/Icons';
import './App.css';

function AppContent() {
  const [currentView, setCurrentView] = useState('dashboard');
  const { user, loading, login, logout } = useAuth();


  const handleLogout = () => {
    logout();
    setCurrentView('dashboard');
  };

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'alerts':
        return <AlertsList />;
      case 'incidents':
        return <IncidentsList />;
      case 'tickets':
        return <TicketsList />;
      case 'soc_tickets':
        return <SOCTicketsList />;
      case 'reports':
        return <Reports />;
      default:
        return <Dashboard />;
    }
  };

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Chargement du portail...</p>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return (
    <div className="App">
      <nav className="app-nav">
        <div className="nav-brand">
          <Logo size="medium" variant="simple" />
        </div>
        
        <div className="nav-menu">
          <button 
            className={`nav-item ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentView('dashboard')}
          >
            <DashboardIcon size={20} color={currentView === 'dashboard' ? '#fff' : '#1A3D6D'} />
            <span>Tableau de bord</span>
          </button>
          <button 
            className={`nav-item ${currentView === 'alerts' ? 'active' : ''}`}
            onClick={() => setCurrentView('alerts')}
          >
            <AlertsIcon size={20} color={currentView === 'alerts' ? '#fff' : '#dc3545'} />
            <span>Alertes</span>
          </button>
          <button 
            className={`nav-item ${currentView === 'incidents' ? 'active' : ''}`}
            onClick={() => setCurrentView('incidents')}
          >
            <IncidentsIcon size={20} color={currentView === 'incidents' ? '#fff' : '#ff6b35'} />
            <span>Incidents</span>
          </button>
          <button 
            className={`nav-item ${currentView === 'tickets' ? 'active' : ''}`}
            onClick={() => setCurrentView('tickets')}
          >
            <TicketsIcon size={20} color={currentView === 'tickets' ? '#fff' : '#28a745'} />
            <span>Mes Tickets</span>
          </button>
          {user && user.role === 'soc_analyst' && (
            <button 
              className={`nav-item ${currentView === 'soc_tickets' ? 'active' : ''}`}
              onClick={() => setCurrentView('soc_tickets')}
            >
              <TicketsIcon size={20} color={currentView === 'soc_tickets' ? '#fff' : '#28a745'} />
              <span>Tickets SOC</span>
            </button>
          )}
          <button
            className={`nav-item ${currentView === 'reports' ? 'active' : ''}`}
            onClick={() => setCurrentView('reports')}
          >
            <ReportsIcon size={20} color={currentView === 'reports' ? '#fff' : '#6f42c1'} />
            <span>Rapports</span>
          </button>
        </div>
        
        <div className="nav-user">
          <span className="user-info">
            <UserIcon size={20} color="#17a2b8" />
            <span>{user?.first_name} {user?.last_name} ({user?.role})</span>
          </span>
          <button className="btn btn-secondary" onClick={handleLogout}>
            <LogoutIcon size={20} color="#6c757d" />
            <span>Déconnexion</span>
          </button>
        </div>
      </nav>
      
      <main className="app-main">
        {renderView()}
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
