import apiClient from './client';

export interface WeatherLocation {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  created_at: string;
  updated_at?: string;
}

export interface WeatherData {
  temperature?: number;
  feels_like?: number;
  condition?: string;
  icon?: string;
  humidity?: number;
  wind_speed?: number;
  wind_direction?: number;
  is_day?: number;
  precipitation?: number;
  last_updated?: string;
  is_stale: boolean;
}

export interface WeatherForecast {
  date: string;
  temperature_max?: number;
  temperature_min?: number;
  condition?: string;
  icon?: string;
}

export const weatherApi = {
  getLocation: async (): Promise<WeatherLocation> => {
    const response = await apiClient.get('/api/weather/location');
    return response.data;
  },

  setLocation: async (data: { name: string; latitude: number; longitude: number }): Promise<WeatherLocation> => {
    const response = await apiClient.post('/api/weather/location', data);
    return response.data;
  },

  getCurrent: async (): Promise<WeatherData> => {
    const response = await apiClient.get('/api/weather/current');
    return response.data;
  },

  getForecast: async (): Promise<WeatherForecast[]> => {
    const response = await apiClient.get('/api/weather/forecast');
    return response.data;
  },

  search: async (query: string): Promise<{ results: any[] }> => {
    const response = await apiClient.get('/api/weather/search', { params: { query } });
    return response.data;
  },
};
