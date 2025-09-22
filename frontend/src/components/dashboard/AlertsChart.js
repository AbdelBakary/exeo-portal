import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const AlertsChart = ({ statistics }) => {
  const data = {
    labels: ['Faible', 'Moyen', 'Élevé', 'Critique'],
    datasets: [
      {
        label: 'Alertes par sévérité',
        data: [
          statistics?.low_severity || 0,
          statistics?.medium_severity || 0,
          statistics?.high_severity || 0,
          statistics?.critical_severity || 0,
        ],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(139, 69, 19, 0.8)',
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(239, 68, 68, 1)',
          'rgba(139, 69, 19, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Répartition des alertes par sévérité',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  return (
    <div className="card">
      <div className="card-body">
        <div className="h-80">
          <Bar data={data} options={options} />
        </div>
      </div>
    </div>
  );
};

export default AlertsChart;
