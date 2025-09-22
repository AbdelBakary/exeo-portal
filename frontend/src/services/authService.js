import api from './api';

export const authService = {
  async login(email, password) {
    const response = await api.post('/auth/login/', { email, password });
    return response.data;
  },

  async logout() {
    const response = await api.post('/auth/logout/');
    return response.data;
  },

  async getProfile() {
    const response = await api.get('/auth/profile/');
    return response.data;
  },

  async updateProfile(profileData) {
    const response = await api.put('/auth/profile/', profileData);
    return response.data;
  },

  async changePassword(oldPassword, newPassword) {
    const response = await api.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password_confirm: newPassword,
    });
    return response.data;
  },

  async refreshToken() {
    const response = await api.post('/auth/refresh-token/');
    return response.data;
  },
};
