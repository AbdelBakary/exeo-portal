import React, { useState, useEffect } from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { useQuery } from 'react-query';
import api from '../../services/api';
import { FiPieChart, FiRefreshCw, FiAlertTriangle } from 'react-icons/fi';

ChartJS.register(ArcElement, Tooltip, Legend);

const RiskScoreChart = () => {
  const { data: distribution, isLoading, error, refetch } = useQuery(
    'risk-score-distribution',
    () => api.get('/analytics/risk-score-distribution/').then(res => res.data),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  const data = {
    labels: ['0-2 (Minimal)', '2-4 (Low)', '4-6 (Medium)', '6-8 (High)', '8-10 (Critical)'],
    datasets: [
      {
        data: distribution?.score_ranges ? [
          distribution.score_ranges['0-2'] || 0,
          distribution.score_ranges['2-4'] || 0,
          distribution.score_ranges['4-6'] || 0,
          distribution.score_ranges['6-8'] || 0,
          distribution.score_ranges['8-10'] || 0,
        ] : [0, 0, 0, 0, 0],
        backgroundColor: [
          '#10b981',   // Green - Minimal
          '#3b82f6',   // Blue - Low
          '#f59e0b',   // Yellow - Medium
          '#ef4444',   // Red - High
          '#dc2626',   // Dark Red - Critical
        ],
        borderColor: [
          '#059669',
          '#2563eb',
          '#d97706',
          '#dc2626',
          '#b91c1c',
        ],
        borderWidth: 3,
        hoverOffset: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '60%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12,
            weight: '600',
          },
          color: '#64748b',
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 12,
        displayColors: true,
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
            return `${label}: ${value} alertes (${percentage}%)`;
          }
        }
      },
    },
  };

  if (isLoading) {
    return (
      <div className="risk-chart-card">
        <div className="risk-chart-header">
          <h3>Scores de Risque</h3>
        </div>
        <div className="risk-chart-body">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Chargement des données...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="risk-chart-card">
        <div className="risk-chart-header">
          <h3>Scores de Risque</h3>
        </div>
        <div className="risk-chart-body">
          <div className="error-container">
            <FiAlertTriangle className="error-icon" />
            <p>Erreur de chargement</p>
            <button className="btn btn-primary" onClick={() => refetch()}>
              <FiRefreshCw className="btn-icon" />
              Réessayer
            </button>
          </div>
        </div>
      </div>
    );
  }

  const totalAlerts = data.datasets[0].data.reduce((a, b) => a + b, 0);

  return (
    <div className="risk-chart-card">
      <div className="risk-chart-header">
        <div className="header-content">
          <div className="header-title">
            <FiPieChart className="header-icon" />
            <h3>Scores de Risque</h3>
          </div>
          <div className="header-badge">
            <span>{totalAlerts} alertes</span>
          </div>
        </div>
        <button className="refresh-btn" onClick={() => refetch()}>
          <FiRefreshCw className="w-4 h-4" />
        </button>
      </div>
      
      <div className="risk-chart-body">
        {totalAlerts > 0 ? (
          <div className="chart-container">
            <div className="chart-wrapper">
              <Doughnut data={data} options={options} />
            </div>
            <div className="chart-summary">
              <div className="summary-item">
                <div className="summary-label">Total</div>
                <div className="summary-value">{totalAlerts}</div>
              </div>
              <div className="summary-item">
                <div className="summary-label">Critiques</div>
                <div className="summary-value critical">{data.datasets[0].data[4] || 0}</div>
              </div>
              <div className="summary-item">
                <div className="summary-label">Élevées</div>
                <div className="summary-value high">{data.datasets[0].data[3] || 0}</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <FiPieChart className="empty-icon" />
            <h4>Aucune donnée</h4>
            <p>Aucune donnée de scoring disponible</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RiskScoreChart;
