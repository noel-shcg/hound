import apiClient from './client';

export interface Photo {
  id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  width?: number;
  height?: number;
  created_at: string;
}

export const photosApi = {
  list: async (): Promise<Photo[]> => {
    const response = await apiClient.get('/api/photos');
    return response.data;
  },

  get: async (id: number): Promise<Photo> => {
    const response = await apiClient.get(`/api/photos/${id}`);
    return response.data;
  },

  upload: async (file: File): Promise<Photo> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/api/photos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/photos/${id}`);
  },

  getUrl: (filename: string): string => {
    return `${apiClient.defaults.baseURL}/photos/${filename}`;
  },
};
