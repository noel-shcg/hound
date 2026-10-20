import apiClient from './client';

export interface Category {
  id: number;
  name: string;
  colour: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

export const categoriesApi = {
  list: async (): Promise<Category[]> => {
    const response = await apiClient.get('/api/categories');
    return response.data;
  },

  get: async (id: number): Promise<Category> => {
    const response = await apiClient.get(`/api/categories/${id}`);
    return response.data;
  },

  create: async (data: Omit<Category, 'id' | 'created_at' | 'updated_at'>): Promise<Category> => {
    const response = await apiClient.post('/api/categories', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Category>): Promise<Category> => {
    const response = await apiClient.put(`/api/categories/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/categories/${id}`);
  },
};
