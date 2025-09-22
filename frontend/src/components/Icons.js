import React from 'react';

export const DashboardIcon = ({ size = 20, color = "#1A3D6D" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="3" width="7" height="7" rx="1" stroke={color} strokeWidth="2" fill="none"/>
    <rect x="14" y="3" width="7" height="7" rx="1" stroke={color} strokeWidth="2" fill="none"/>
    <rect x="3" y="14" width="7" height="7" rx="1" stroke={color} strokeWidth="2" fill="none"/>
    <rect x="14" y="14" width="7" height="7" rx="1" stroke={color} strokeWidth="2" fill="none"/>
  </svg>
);

export const AlertsIcon = ({ size = 20, color = "#dc3545" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2L2 7l10 5 10-5-10-5z" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M2 17l10 5 10-5" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M2 12l10 5 10-5" stroke={color} strokeWidth="2" fill="none"/>
  </svg>
);

export const IncidentsIcon = ({ size = 20, color = "#ff6b35" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="4" width="18" height="15" rx="2" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M7 8h10M7 12h10M7 16h6" stroke={color} strokeWidth="2" strokeLinecap="round"/>
  </svg>
);

export const TicketsIcon = ({ size = 20, color = "#28a745" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="4" width="18" height="16" rx="2" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M8 8h8M8 12h8M8 16h4" stroke={color} strokeWidth="2" strokeLinecap="round"/>
    <circle cx="18" cy="6" r="2" fill={color}/>
  </svg>
);

export const ReportsIcon = ({ size = 20, color = "#6f42c1" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke={color} strokeWidth="2" fill="none"/>
    <polyline points="14,2 14,8 20,8" stroke={color} strokeWidth="2" fill="none"/>
    <line x1="16" y1="13" x2="8" y2="13" stroke={color} strokeWidth="2"/>
    <line x1="16" y1="17" x2="8" y2="17" stroke={color} strokeWidth="2"/>
    <polyline points="10,9 9,9 8,9" stroke={color} strokeWidth="2"/>
  </svg>
);

export const SecurityIcon = ({ size = 20, color = "#1A3D6D" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M9 12l2 2 4-4" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const UserIcon = ({ size = 20, color = "#17a2b8" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke={color} strokeWidth="2" fill="none"/>
    <circle cx="12" cy="7" r="4" stroke={color} strokeWidth="2" fill="none"/>
  </svg>
);

export const LogoutIcon = ({ size = 20, color = "#6c757d" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke={color} strokeWidth="2" fill="none"/>
    <polyline points="16,17 21,12 16,7" stroke={color} strokeWidth="2" fill="none"/>
    <line x1="21" y1="12" x2="9" y2="12" stroke={color} strokeWidth="2"/>
  </svg>
);

export const PlusIcon = ({ size = 20, color = "#fff" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <line x1="12" y1="5" x2="12" y2="19" stroke={color} strokeWidth="2"/>
    <line x1="5" y1="12" x2="19" y2="12" stroke={color} strokeWidth="2"/>
  </svg>
);

export const SearchIcon = ({ size = 20, color = "#666" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="11" cy="11" r="8" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M21 21l-4.35-4.35" stroke={color} strokeWidth="2" strokeLinecap="round"/>
  </svg>
);

export const FilterIcon = ({ size = 20, color = "#666" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46 22,3" stroke={color} strokeWidth="2" fill="none"/>
  </svg>
);

