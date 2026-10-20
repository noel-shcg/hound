import apiClient from './client';

export interface LoginRequest {
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CredentialCreate {
  password: string;
}

export const authApi = {
  setup: async (data: CredentialCreate) => {
    const response = await apiClient.post('/api/auth/setup', data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post('/api/auth/login', data);
    // Store token
    localStorage.setItem('auth_token', response.data.access_token);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('auth_token');
  },

  changePassword: async (newPassword: string) => {
    const response = await apiClient.post('/api/auth/change-password', newPassword, {
      headers: { 'Content-Type': 'text/plain' }
    });
    return response.data;
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('auth_token');
  },
};
