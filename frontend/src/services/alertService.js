import api from './api';

export const alertService = {
  async getAlerts(params = {}) {
    const response = await api.get('/alerts/', { params });
    return response.data;
  },

  async getAlert(id) {
    const response = await api.get(`/alerts/${id}/`);
    return response.data;
  },

  async createAlert(alertData) {
    const response = await api.post('/alerts/', alertData);
    return response.data;
  },

  async updateAlert(id, alertData) {
    const response = await api.put(`/alerts/${id}/`, alertData);
    return response.data;
  },

  async deleteAlert(id) {
    const response = await api.delete(`/alerts/${id}/`);
    return response.data;
  },

  async assignAlert(id, userId) {
    const response = await api.post(`/alerts/${id}/assign/`, { assigned_to: userId });
    return response.data;
  },

  async getAlertStatistics() {
    const response = await api.get('/alerts/statistics/');
    return response.data;
  },

  async bulkUpdateAlerts(alertIds, updates) {
    const response = await api.post('/alerts/bulk-update/', {
      alert_ids: alertIds,
      updates: updates,
    });
    return response.data;
  },

  async getAlertComments(alertId) {
    const response = await api.get(`/alerts/${alertId}/comments/`);
    return response.data;
  },

  async createAlertComment(alertId, commentData) {
    const response = await api.post(`/alerts/${alertId}/comments/`, commentData);
    return response.data;
  },

  async getAlertAttachments(alertId) {
    const response = await api.get(`/alerts/${alertId}/attachments/`);
    return response.data;
  },

  async uploadAlertAttachment(alertId, file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/alerts/${alertId}/attachments/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getAlertRules() {
    const response = await api.get('/alerts/rules/');
    return response.data;
  },

  async createAlertRule(ruleData) {
    const response = await api.post('/alerts/rules/', ruleData);
    return response.data;
  },

  async updateAlertRule(id, ruleData) {
    const response = await api.put(`/alerts/rules/${id}/`, ruleData);
    return response.data;
  },

  async deleteAlertRule(id) {
    const response = await api.delete(`/alerts/rules/${id}/`);
    return response.data;
  },
};
