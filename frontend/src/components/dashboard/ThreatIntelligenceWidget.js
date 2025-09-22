import React from 'react';
import { FiShield, FiTrendingUp, FiAlertCircle } from 'react-icons/fi';

const ThreatIntelligenceWidget = () => {
  // Mock data - would come from API
  const threatData = {
    totalIndicators: 1247,
    newToday: 23,
    highConfidence: 156,
    correlations: 89,
  };

  const recentThreats = [
    {
      id: 1,
      type: 'Malware',
      indicator: '192.168.1.100',
      confidence: 'high',
      source: 'MISP',
    },
    {
      id: 2,
      type: 'Phishing',
      indicator: 'suspicious-domain.com',
      confidence: 'medium',
      source: 'CERT-FR',
    },
    {
      id: 3,
      type: 'APT',
      indicator: 'malware-hash-abc123',
      confidence: 'high',
      source: 'OSINT',
    },
  ];

  const getConfidenceColor = (confidence) => {
    const colors = {
      low: 'text-yellow-600 bg-yellow-100',
      medium: 'text-orange-600 bg-orange-100',
      high: 'text-red-600 bg-red-100',
    };
    return colors[confidence] || 'text-gray-600 bg-gray-100';
  };

  const getConfidenceLabel = (confidence) => {
    const labels = {
      low: 'Faible',
      medium: 'Moyen',
      high: 'Élevé',
    };
    return labels[confidence] || confidence;
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center">
          <FiShield className="w-5 h-5 text-primary mr-2" />
          <h3 className="text-lg font-semibold">Threat Intelligence</h3>
        </div>
      </div>
      <div className="card-body">
        {/* Statistics */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">{threatData.totalIndicators}</div>
            <div className="text-sm text-gray-600">Indicateurs totaux</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{threatData.newToday}</div>
            <div className="text-sm text-gray-600">Nouveaux aujourd'hui</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{threatData.highConfidence}</div>
            <div className="text-sm text-gray-600">Haute confiance</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{threatData.correlations}</div>
            <div className="text-sm text-gray-600">Corrélations</div>
          </div>
        </div>

        {/* Recent threats */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Menaces récentes</h4>
          <div className="space-y-3">
            {recentThreats.map((threat) => (
              <div key={threat.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <FiAlertCircle className="w-4 h-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-900">{threat.type}</span>
                  </div>
                  <p className="text-xs text-gray-600 truncate">{threat.indicator}</p>
                  <p className="text-xs text-gray-500">{threat.source}</p>
                </div>
                <span
                  className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(
                    threat.confidence
                  )}`}
                >
                  {getConfidenceLabel(threat.confidence)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Action button */}
        <div className="mt-4">
          <button className="btn btn-secondary w-full">
            <FiTrendingUp className="w-4 h-4" />
            Voir toutes les menaces
          </button>
        </div>
      </div>
    </div>
  );
};

export default ThreatIntelligenceWidget;
