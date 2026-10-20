import apiClient from './client';
import type { Category } from './categories';

export interface Event {
  id: number;
  title: string;
  start_datetime: string;
  end_datetime?: string;
  all_day: boolean;
  notes?: string;
  category_id?: number;
  is_recurring: boolean;
  created_at: string;
  updated_at?: string;
  category?: Category;
  recurrence_rule?: RecurrenceRule;
}

export interface RecurrenceRule {
  id: number;
  event_id: number;
  frequency: string;
  interval: number;
  weekdays?: number[];
  end_date?: string;
  occurrence_limit?: number;
  created_at: string;
  updated_at?: string;
}

export const eventsApi = {
  list: async (startDate?: string, endDate?: string): Promise<Event[]> => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await apiClient.get('/api/events', { params });
    return response.data;
  },

  get: async (id: number): Promise<Event> => {
    const response = await apiClient.get(`/api/events/${id}`);
    return response.data;
  },

  create: async (data: Omit<Event, 'id' | 'created_at' | 'updated_at'>): Promise<Event> => {
    const response = await apiClient.post('/api/events', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Event>): Promise<Event> => {
    const response = await apiClient.put(`/api/events/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/events/${id}`);
  },

  getOccurrences: async (startDate: string, endDate: string): Promise<{ occurrences: Event[] }> => {
    const response = await apiClient.get('/api/events/recurring/occurrences', {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  },
};
