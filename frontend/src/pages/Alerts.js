import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { alertService } from '../services/alertService';
import AlertsTable from '../components/alerts/AlertsTable';
import AlertsFilters from '../components/alerts/AlertsFilters';
import LoadingSpinner from '../components/LoadingSpinner';

const Alerts = () => {
  const [filters, setFilters] = useState({
    search: '',
    severity: '',
    status: '',
    alert_type: '',
    min_risk_score: '',
    max_risk_score: '',
    page: 1,
  });

  const { data: alerts, isLoading, refetch } = useQuery(
    ['alerts', filters],
    () => alertService.getAlerts(filters),
    {
      keepPreviousData: true,
    }
  );

  const handleFilterChange = (newFilters) => {
    setFilters({ ...filters, ...newFilters, page: 1 });
  };

  const handlePageChange = (page) => {
    setFilters({ ...filters, page });
  };

  if (isLoading) {
    return <LoadingSpinner text="Chargement des alertes..." />;
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-primary">Alertes de sécurité</h1>
        <p className="text-gray-600">
          Gestion et suivi des alertes de sécurité
        </p>
      </div>

      {/* Filters */}
      <AlertsFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onRefresh={refetch}
      />

      {/* Alerts table */}
      <AlertsTable
        alerts={alerts}
        onPageChange={handlePageChange}
        onRefresh={refetch}
      />
    </div>
  );
};

export default Alerts;
