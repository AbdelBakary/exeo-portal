import React from 'react';

const LoadingSpinner = ({ size = 'md', text = 'Chargement...' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-secondary">
      <div className={`spinner ${sizeClasses[size]}`}></div>
      {text && (
        <p className="mt-4 text-sm text-gray-600">{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
