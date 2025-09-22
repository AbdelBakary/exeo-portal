import React, { useState } from 'react';
import { FiSearch, FiFilter, FiRefreshCw, FiX } from 'react-icons/fi';

const AlertsFilters = ({ filters, onFilterChange, onRefresh }) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleInputChange = (field, value) => {
    onFilterChange({ [field]: value });
  };

  const handleSelectChange = (field, value) => {
    onFilterChange({ [field]: value });
  };

  const clearFilters = () => {
    onFilterChange({
      search: '',
      severity: '',
      status: '',
      alert_type: '',
      min_risk_score: '',
      max_risk_score: '',
    });
  };

  const hasActiveFilters = Object.values(filters).some(value => value && value !== '');

  return (
    <div className="card">
      <div className="card-body">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          {/* Search and basic filters */}
          <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 flex-1">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FiSearch className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Rechercher dans les alertes..."
                value={filters.search}
                onChange={(e) => handleInputChange('search', e.target.value)}
                className="form-input pl-10"
              />
            </div>

            {/* Severity filter */}
            <select
              value={filters.severity}
              onChange={(e) => handleSelectChange('severity', e.target.value)}
              className="form-select"
            >
              <option value="">Toutes les sévérités</option>
              <option value="low">Faible</option>
              <option value="medium">Moyen</option>
              <option value="high">Élevé</option>
              <option value="critical">Critique</option>
            </select>

            {/* Status filter */}
            <select
              value={filters.status}
              onChange={(e) => handleSelectChange('status', e.target.value)}
              className="form-select"
            >
              <option value="">Tous les statuts</option>
              <option value="open">Ouvert</option>
              <option value="in_progress">En cours</option>
              <option value="closed">Fermé</option>
              <option value="false_positive">Faux positif</option>
            </select>
          </div>

          {/* Action buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="btn btn-secondary btn-sm"
            >
              <FiFilter className="w-4 h-4" />
              Filtres avancés
            </button>
            
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="btn btn-secondary btn-sm"
              >
                <FiX className="w-4 h-4" />
                Effacer
              </button>
            )}
            
            <button
              onClick={onRefresh}
              className="btn btn-primary btn-sm"
            >
              <FiRefreshCw className="w-4 h-4" />
              Actualiser
            </button>
          </div>
        </div>

        {/* Advanced filters */}
        {showAdvanced && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Alert type filter */}
              <div>
                <label className="form-label">Type d'alerte</label>
                <select
                  value={filters.alert_type}
                  onChange={(e) => handleSelectChange('alert_type', e.target.value)}
                  className="form-select"
                >
                  <option value="">Tous les types</option>
                  <option value="malware">Malware</option>
                  <option value="phishing">Phishing</option>
                  <option value="ddos">DDoS</option>
                  <option value="intrusion">Intrusion</option>
                  <option value="data_exfiltration">Exfiltration de données</option>
                  <option value="privilege_escalation">Élévation de privilèges</option>
                  <option value="suspicious_activity">Activité suspecte</option>
                  <option value="vulnerability">Vulnérabilité</option>
                  <option value="policy_violation">Violation de politique</option>
                  <option value="other">Autre</option>
                </select>
              </div>

              {/* Min risk score */}
              <div>
                <label className="form-label">Score de risque min</label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  step="0.1"
                  value={filters.min_risk_score}
                  onChange={(e) => handleInputChange('min_risk_score', e.target.value)}
                  className="form-input"
                  placeholder="0.0"
                />
              </div>

              {/* Max risk score */}
              <div>
                <label className="form-label">Score de risque max</label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  step="0.1"
                  value={filters.max_risk_score}
                  onChange={(e) => handleInputChange('max_risk_score', e.target.value)}
                  className="form-input"
                  placeholder="10.0"
                />
              </div>

              {/* Date range (placeholder for future implementation) */}
              <div>
                <label className="form-label">Période</label>
                <select className="form-select">
                  <option value="">Toutes les périodes</option>
                  <option value="today">Aujourd'hui</option>
                  <option value="week">Cette semaine</option>
                  <option value="month">Ce mois</option>
                  <option value="quarter">Ce trimestre</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertsFilters;
