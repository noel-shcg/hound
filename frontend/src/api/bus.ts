import apiClient from './client';

export interface BusStop {
  id: number;
  atco_code: string;
  custom_label: string;
  official_name?: string;
  enabled: boolean;
  display_order: number;
  created_at: string;
  updated_at?: string;
}

export interface BusDeparture {
  route?: string;
  destination?: string;
  scheduled_time?: string;
  countdown_minutes?: number;
  status?: string;
}

export const busApi = {
  list: async (): Promise<BusStop[]> => {
    const response = await apiClient.get('/api/bus-stops');
    return response.data;
  },

  get: async (id: number): Promise<BusStop> => {
    const response = await apiClient.get(`/api/bus-stops/${id}`);
    return response.data;
  },

  create: async (data: Omit<BusStop, 'id' | 'created_at' | 'updated_at'>): Promise<BusStop> => {
    const response = await apiClient.post('/api/bus-stops', data);
    return response.data;
  },

  update: async (id: number, data: Partial<BusStop>): Promise<BusStop> => {
    const response = await apiClient.put(`/api/bus-stops/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/bus-stops/${id}`);
  },

  getDepartures: async (id: number): Promise<BusDeparture[]> => {
    const response = await apiClient.get(`/api/bus-stops/${id}/departures`);
    return response.data;
  },
};
