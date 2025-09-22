import React, { useState, useEffect } from 'react';
import './Reports.css';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportData, setReportData] = useState(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      // Simulate fetching reports - in real app, this would call the API
      const mockReports = [
        {
          id: 1,
          name: 'Rapport de sécurité mensuel',
          type: 'monthly',
          period: '2024-01',
          status: 'completed',
          created_at: '2024-01-31T10:00:00Z',
          file_size: '2.3 MB',
          download_count: 15
        },
        {
          id: 2,
          name: 'Analyse des incidents critiques',
          type: 'incident_analysis',
          period: '2024-01-15',
          status: 'completed',
          created_at: '2024-01-20T14:30:00Z',
          file_size: '1.8 MB',
          download_count: 8
        },
        {
          id: 3,
          name: 'Rapport de conformité RGPD',
          type: 'compliance',
          period: '2024-Q1',
          status: 'in_progress',
          created_at: '2024-01-25T09:15:00Z',
          file_size: null,
          download_count: 0
        },
        {
          id: 4,
          name: 'Audit de sécurité trimestriel',
          type: 'audit',
          period: '2024-Q1',
          status: 'scheduled',
          created_at: '2024-01-01T00:00:00Z',
          file_size: null,
          download_count: 0
        }
      ];
      
      setReports(mockReports);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (reportType) => {
    try {
      setLoading(true);
      // Simulate report generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const newReport = {
        id: reports.length + 1,
        name: `Rapport ${reportType} - ${new Date().toLocaleDateString('fr-FR')}`,
        type: reportType,
        period: new Date().toISOString().split('T')[0],
        status: 'completed',
        created_at: new Date().toISOString(),
        file_size: '1.5 MB',
        download_count: 0
      };
      
      setReports(prev => [newReport, ...prev]);
    } catch (err) {
      setError('Erreur lors de la génération du rapport');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = (report) => {
    // Simulate download
    const link = document.createElement('a');
    link.href = `#download-${report.id}`;
    link.download = `${report.name}.pdf`;
    link.click();
  };

  const getStatusColor = (status) => {
    const colors = {
      'completed': '#28a745',
      'in_progress': '#ffc107',
      'scheduled': '#17a2b8',
      'failed': '#dc3545'
    };
    return colors[status] || '#6c757d';
  };

  const getStatusText = (status) => {
    const texts = {
      'completed': 'Terminé',
      'in_progress': 'En cours',
      'scheduled': 'Programmé',
      'failed': 'Échec'
    };
    return texts[status] || status;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('fr-FR');
  };

  if (loading) {
    return (
      <div className="reports-loading">
        <div className="loading-spinner"></div>
        <p>Chargement des rapports...</p>
      </div>
    );
  }

  return (
    <div className="reports">
      <div className="reports-header">
        <h1>Rapports de sécurité</h1>
        <div className="reports-actions">
          <button 
            className="btn btn-primary"
            onClick={() => generateReport('monthly')}
            disabled={loading}
          >
            {loading ? 'Génération...' : 'Générer rapport mensuel'}
          </button>
        </div>
      </div>

      {/* Statistiques des rapports */}
      <div className="reports-stats">
        <div className="stat-card">
          <h3>Rapports générés</h3>
          <p className="stat-value">{reports.length}</p>
        </div>
        <div className="stat-card">
          <h3>Rapports terminés</h3>
          <p className="stat-value">{reports.filter(r => r.status === 'completed').length}</p>
        </div>
        <div className="stat-card">
          <h3>Téléchargements totaux</h3>
          <p className="stat-value">{reports.reduce((sum, r) => sum + r.download_count, 0)}</p>
        </div>
        <div className="stat-card">
          <h3>Espace utilisé</h3>
          <p className="stat-value">
            {reports
              .filter(r => r.file_size)
              .reduce((sum, r) => sum + parseFloat(r.file_size), 0)
              .toFixed(1)} MB
          </p>
        </div>
      </div>

      {/* Liste des rapports */}
      <div className="reports-list">
        <div className="reports-list-header">
          <h2>Rapports disponibles</h2>
          <div className="report-filters">
            <select>
              <option value="">Tous les types</option>
              <option value="monthly">Mensuel</option>
              <option value="incident_analysis">Analyse d'incidents</option>
              <option value="compliance">Conformité</option>
              <option value="audit">Audit</option>
            </select>
            <select>
              <option value="">Tous les statuts</option>
              <option value="completed">Terminé</option>
              <option value="in_progress">En cours</option>
              <option value="scheduled">Programmé</option>
            </select>
          </div>
        </div>

        <div className="reports-grid">
          {reports.map((report) => (
            <div key={report.id} className="report-card">
              <div className="report-header">
                <h3>{report.name}</h3>
                <span 
                  className="report-status"
                  style={{ backgroundColor: getStatusColor(report.status) }}
                >
                  {getStatusText(report.status)}
                </span>
              </div>
              
              <div className="report-details">
                <div className="report-detail">
                  <strong>Type:</strong> {report.type}
                </div>
                <div className="report-detail">
                  <strong>Période:</strong> {report.period}
                </div>
                <div className="report-detail">
                  <strong>Créé le:</strong> {formatDate(report.created_at)}
                </div>
                {report.file_size && (
                  <div className="report-detail">
                    <strong>Taille:</strong> {report.file_size}
                  </div>
                )}
                <div className="report-detail">
                  <strong>Téléchargements:</strong> {report.download_count}
                </div>
              </div>
              
              <div className="report-actions">
                {report.status === 'completed' ? (
                  <button 
                    className="btn btn-primary"
                    onClick={() => downloadReport(report)}
                  >
                    📥 Télécharger
                  </button>
                ) : report.status === 'in_progress' ? (
                  <button className="btn btn-secondary" disabled>
                    ⏳ En cours...
                  </button>
                ) : (
                  <button className="btn btn-secondary" disabled>
                    📅 Programmé
                  </button>
                )}
                
                <button 
                  className="btn btn-outline"
                  onClick={() => setSelectedReport(report)}
                >
                  👁️ Voir détails
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal de détails du rapport */}
      {selectedReport && (
        <div className="report-modal">
          <div className="report-modal-content">
            <div className="report-modal-header">
              <h2>{selectedReport.name}</h2>
              <button 
                className="close-button"
                onClick={() => setSelectedReport(null)}
              >
                ✕
              </button>
            </div>
            
            <div className="report-modal-body">
              <div className="report-info">
                <h3>Informations du rapport</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <strong>Type:</strong> {selectedReport.type}
                  </div>
                  <div className="info-item">
                    <strong>Période:</strong> {selectedReport.period}
                  </div>
                  <div className="info-item">
                    <strong>Statut:</strong> 
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(selectedReport.status) }}
                    >
                      {getStatusText(selectedReport.status)}
                    </span>
                  </div>
                  <div className="info-item">
                    <strong>Créé le:</strong> {formatDate(selectedReport.created_at)}
                  </div>
                  {selectedReport.file_size && (
                    <div className="info-item">
                      <strong>Taille du fichier:</strong> {selectedReport.file_size}
                    </div>
                  )}
                  <div className="info-item">
                    <strong>Téléchargements:</strong> {selectedReport.download_count}
                  </div>
                </div>
              </div>
              
              {selectedReport.status === 'completed' && (
                <div className="report-preview">
                  <h3>Aperçu du rapport</h3>
                  <div className="preview-placeholder">
                    <p>Aperçu du rapport PDF</p>
                    <p>Le rapport contient des graphiques, des statistiques et des analyses détaillées.</p>
                  </div>
                </div>
              )}
            </div>
            
            <div className="report-modal-footer">
              {selectedReport.status === 'completed' && (
                <button 
                  className="btn btn-primary"
                  onClick={() => downloadReport(selectedReport)}
                >
                  📥 Télécharger le rapport
                </button>
              )}
              <button 
                className="btn btn-secondary"
                onClick={() => setSelectedReport(null)}
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="reports-error">
          <h3>Erreur</h3>
          <p>{error}</p>
          <button onClick={fetchReports}>Réessayer</button>
        </div>
      )}
    </div>
  );
};

export default Reports;
