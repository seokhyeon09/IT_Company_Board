import { apiClient } from './client';
import { EmailNotificationItem } from '../features/ticket/types/ticket';

export const notificationApi = {
  getNotifications: async (limit = 100): Promise<{ notifications: EmailNotificationItem[] }> => {
    const response = await apiClient.get<{ notifications: EmailNotificationItem[] }>('/notifications', {
      params: { limit },
    });
    return response.data;
  },

  markAsRead: async (notificationId: string): Promise<{ success: boolean }> => {
    const response = await apiClient.post<{ success: boolean }>('/notifications/read', {
      notification_id: notificationId,
    });
    return response.data;
  },

  markAllAsRead: async (): Promise<{ success: boolean }> => {
    const response = await apiClient.post<{ success: boolean }>('/notifications/read-all');
    return response.data;
  },
};
