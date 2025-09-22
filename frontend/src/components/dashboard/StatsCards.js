import React from 'react';
import { FiAlertTriangle, FiCheckCircle, FiClock, FiTrendingUp, FiArrowUp, FiArrowDown, FiMinus } from 'react-icons/fi';

const StatsCards = ({ statistics }) => {
  const cards = [
    {
      title: 'Total des alertes',
      value: statistics?.total_alerts || 0,
      icon: FiAlertTriangle,
      gradient: 'from-blue-500 to-blue-600',
      bgGradient: 'from-blue-50 to-blue-100',
      textColor: 'text-blue-600',
      trend: 'stable',
      trendValue: '+2.5%',
    },
    {
      title: 'Alertes ouvertes',
      value: statistics?.open_alerts || 0,
      icon: FiClock,
      gradient: 'from-orange-500 to-orange-600',
      bgGradient: 'from-orange-50 to-orange-100',
      textColor: 'text-orange-600',
      trend: 'up',
      trendValue: '+12.3%',
    },
    {
      title: 'Alertes fermées',
      value: statistics?.closed_alerts || 0,
      icon: FiCheckCircle,
      gradient: 'from-green-500 to-green-600',
      bgGradient: 'from-green-50 to-green-100',
      textColor: 'text-green-600',
      trend: 'up',
      trendValue: '+8.7%',
    },
    {
      title: 'Score de risque moyen',
      value: statistics?.avg_risk_score?.toFixed(1) || '0.0',
      icon: FiTrendingUp,
      gradient: 'from-red-500 to-red-600',
      bgGradient: 'from-red-50 to-red-100',
      textColor: 'text-red-600',
      trend: 'down',
      trendValue: '-1.2%',
      unit: '/10',
    },
  ];

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return <FiArrowUp className="w-3 h-3" />;
      case 'down':
        return <FiArrowDown className="w-3 h-3" />;
      default:
        return <FiMinus className="w-3 h-3" />;
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'up':
        return 'text-green-600 bg-green-100';
      case 'down':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="stats-cards-grid">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <div key={index} className="stats-card">
            <div className="stats-card-content">
              <div className="stats-card-header">
                <div className={`stats-icon ${card.gradient}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div className={`trend-indicator ${getTrendColor(card.trend)}`}>
                  {getTrendIcon(card.trend)}
                  <span className="trend-text">{card.trendValue}</span>
                </div>
              </div>
              
              <div className="stats-card-body">
                <div className="stats-value">
                  {card.value}
                  {card.unit && <span className="stats-unit">{card.unit}</span>}
                </div>
                <div className="stats-title">{card.title}</div>
              </div>
              
              <div className="stats-card-footer">
                <div className={`progress-bar ${card.bgGradient}`}>
                  <div 
                    className={`progress-fill ${card.gradient}`}
                    style={{ width: `${Math.min((card.value / 50) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StatsCards;
