import React from 'react';
import './Logo.css';

const Logo = ({ size = 'medium', showText = true, variant = 'full' }) => {
  return (
    <div className={`logo-container ${size}`}>
      <div className="logo-icon">
        <img 
          src="https://exeo.net/wp-content/uploads/2022/02/cropped-EXEO-WP.png" 
          alt="EXEO Logo" 
          className="exeo-logo"
        />
      </div>
      {showText && (
        <div className="logo-text">
          {variant === 'full' ? (
            <>
              <span className="logo-primary">EXEO</span>
              <span className="logo-secondary">Security Portal</span>
            </>
          ) : (
            <span className="logo-simple">Security Portal</span>
          )}
        </div>
      )}
    </div>
  );
};

export default Logo;
