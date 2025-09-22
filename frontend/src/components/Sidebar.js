import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import {
  FiHome,
  FiAlertTriangle,
  FiAlertCircle,
  FiShield,
  FiFileText,
  FiSettings,
  FiX,
} from 'react-icons/fi';

const Sidebar = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const location = useLocation();

  const navigation = [
    { name: 'Tableau de bord', href: '/dashboard', icon: FiHome },
    { name: 'Alertes', href: '/alerts', icon: FiAlertTriangle },
    { name: 'Incidents', href: '/incidents', icon: FiAlertCircle },
    { name: 'Threat Intelligence', href: '/threat-intelligence', icon: FiShield },
    { name: 'Rapports', href: '/reports', icon: FiFileText },
    { name: 'Paramètres', href: '/settings', icon: FiSettings },
  ];

  const isCurrentPath = (path) => {
    return location.pathname === path;
  };

  return (
    <>
      {/* Mobile sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:hidden ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">E</span>
            </div>
            <span className="ml-2 text-xl font-bold text-primary">EXEO</span>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
          >
            <FiX className="w-6 h-6" />
          </button>
        </div>

        <nav className="mt-6 px-3">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={onClose}
                className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 transition-colors ${
                  isCurrentPath(item.href)
                    ? 'bg-primary text-white'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-primary'
                }`}
              >
                <Icon
                  className={`mr-3 h-5 w-5 ${
                    isCurrentPath(item.href) ? 'text-white' : 'text-gray-400 group-hover:text-primary'
                  }`}
                />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User info */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-gray-700">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">
                {user?.get_full_name || user?.email}
              </p>
              <p className="text-xs text-gray-500 capitalize">
                {user?.role?.replace('_', ' ')}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
          <div className="flex items-center h-16 px-6 border-b border-gray-200">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">E</span>
            </div>
            <span className="ml-2 text-xl font-bold text-primary">EXEO</span>
          </div>

          <nav className="mt-6 flex-1 px-3 pb-4 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 transition-colors ${
                    isCurrentPath(item.href)
                      ? 'bg-primary text-white'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-primary'
                  }`}
                >
                  <Icon
                    className={`mr-3 h-5 w-5 ${
                      isCurrentPath(item.href) ? 'text-white' : 'text-gray-400 group-hover:text-primary'
                    }`}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* User info */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-gray-700">
                  {user?.first_name?.[0]}{user?.last_name?.[0]}
                </span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">
                  {user?.get_full_name || user?.email}
                </p>
                <p className="text-xs text-gray-500 capitalize">
                  {user?.role?.replace('_', ' ')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
