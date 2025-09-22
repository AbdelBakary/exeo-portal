import React from 'react';
import { useQuery } from 'react-query';
import { alertService } from '../services/alertService';
import StatsCards from '../components/dashboard/StatsCards';
import AlertsChart from '../components/dashboard/AlertsChart';
import RiskScoreChart from '../components/dashboard/RiskScoreChart';
import RecentAlerts from '../components/dashboard/RecentAlerts';
import ThreatIntelligenceWidget from '../components/dashboard/ThreatIntelligenceWidget';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard = () => {
  const { data: statistics, isLoading: statsLoading } = useQuery(
    'alertStatistics',
    alertService.getAlertStatistics,
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  if (statsLoading) {
    return <LoadingSpinner text="Chargement du tableau de bord..." />;
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-primary">Tableau de bord</h1>
        <p className="text-gray-600">
          Vue d'ensemble de votre posture de sécurité
        </p>
      </div>

      {/* Statistics cards */}
      <StatsCards statistics={statistics} />

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AlertsChart statistics={statistics} />
        <RiskScoreChart statistics={statistics} />
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RecentAlerts />
        </div>
        <div>
          <ThreatIntelligenceWidget />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
