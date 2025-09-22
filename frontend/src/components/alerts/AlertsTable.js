import React from 'react';
import { Link } from 'react-router-dom';
import { FiEye, FiEdit, FiUser, FiClock } from 'react-icons/fi';

const AlertsTable = ({ alerts, onPageChange, onRefresh }) => {
  const getSeverityColor = (severity) => {
    const colors = {
      low: 'text-green-600 bg-green-100',
      medium: 'text-yellow-600 bg-yellow-100',
      high: 'text-orange-600 bg-orange-100',
      critical: 'text-red-600 bg-red-100',
    };
    return colors[severity] || 'text-gray-600 bg-gray-100';
  };

  const getSeverityLabel = (severity) => {
    const labels = {
      low: 'Faible',
      medium: 'Moyen',
      high: 'Élevé',
      critical: 'Critique',
    };
    return labels[severity] || severity;
  };

  const getStatusColor = (status) => {
    const colors = {
      open: 'text-red-600 bg-red-100',
      in_progress: 'text-yellow-600 bg-yellow-100',
      closed: 'text-green-600 bg-green-100',
      false_positive: 'text-gray-600 bg-gray-100',
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
  };

  const getStatusLabel = (status) => {
    const labels = {
      open: 'Ouvert',
      in_progress: 'En cours',
      closed: 'Fermé',
      false_positive: 'Faux positif',
    };
    return labels[status] || status;
  };

  const getAlertTypeLabel = (type) => {
    const labels = {
      malware: 'Malware',
      phishing: 'Phishing',
      ddos: 'DDoS',
      intrusion: 'Intrusion',
      data_exfiltration: 'Exfiltration',
      privilege_escalation: 'Élévation de privilèges',
      suspicious_activity: 'Activité suspecte',
      vulnerability: 'Vulnérabilité',
      policy_violation: 'Violation de politique',
      other: 'Autre',
    };
    return labels[type] || type;
  };

  if (!alerts?.results?.length) {
    return (
      <div className="card">
        <div className="card-body text-center py-12">
          <div className="text-gray-400 mb-4">
            <FiEye className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune alerte trouvée</h3>
          <p className="text-gray-500">Aucune alerte ne correspond aux critères de recherche.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-body p-0">
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Titre</th>
                <th>Type</th>
                <th>Sévérité</th>
                <th>Statut</th>
                <th>Score de risque</th>
                <th>Assigné à</th>
                <th>Détecté le</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {alerts.results.map((alert) => (
                <tr key={alert.id}>
                  <td className="font-mono text-sm">{alert.alert_id}</td>
                  <td>
                    <div className="max-w-xs">
                      <p className="font-medium text-gray-900 truncate">{alert.title}</p>
                      <p className="text-sm text-gray-500 truncate">{alert.description}</p>
                    </div>
                  </td>
                  <td>
                    <span className="text-sm text-gray-600">
                      {getAlertTypeLabel(alert.alert_type)}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(
                        alert.severity
                      )}`}
                    >
                      {getSeverityLabel(alert.severity)}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                        alert.status
                      )}`}
                    >
                      {getStatusLabel(alert.status)}
                    </span>
                  </td>
                  <td>
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-primary h-2 rounded-full"
                          style={{ width: `${(alert.risk_score / 10) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{alert.risk_score?.toFixed(1) || 'N/A'}</span>
                    </div>
                  </td>
                  <td>
                    {alert.assigned_to_name ? (
                      <div className="flex items-center">
                        <FiUser className="w-4 h-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-600">{alert.assigned_to_name}</span>
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">Non assigné</span>
                    )}
                  </td>
                  <td>
                    <div className="flex items-center text-sm text-gray-600">
                      <FiClock className="w-4 h-4 mr-1" />
                      {new Date(alert.detected_at).toLocaleDateString('fr-FR')}
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center space-x-2">
                      <Link
                        to={`/alerts/${alert.id}`}
                        className="p-1 text-gray-400 hover:text-primary"
                        title="Voir les détails"
                      >
                        <FiEye className="w-4 h-4" />
                      </Link>
                      <button
                        className="p-1 text-gray-400 hover:text-primary"
                        title="Modifier"
                      >
                        <FiEdit className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {alerts.count > 20 && (
          <div className="px-6 py-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Affichage de {((alerts.current_page - 1) * 20) + 1} à {Math.min(alerts.current_page * 20, alerts.count)} sur {alerts.count} résultats
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onPageChange(alerts.current_page - 1)}
                  disabled={!alerts.previous}
                  className="btn btn-secondary btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Précédent
                </button>
                <span className="text-sm text-gray-600">
                  Page {alerts.current_page} sur {Math.ceil(alerts.count / 20)}
                </span>
                <button
                  onClick={() => onPageChange(alerts.current_page + 1)}
                  disabled={!alerts.next}
                  className="btn btn-secondary btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Suivant
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertsTable;
