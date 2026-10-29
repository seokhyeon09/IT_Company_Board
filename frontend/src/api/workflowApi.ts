import { apiClient } from './client';
import { TicketDetail } from '../features/ticket/types/ticket';

export interface ResolveTicketPayload {
  resolution_note: string;
  is_faq?: boolean;
  expected_write_date?: string;
}

export const workflowApi = {
  assignSelf: async (id: number): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/assign-self`);
    return response.data;
  },

  assignOfficer: async (id: number, officerId: number, reason?: string): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/assign`, {
      assignee_id: officerId,
      officer_id: officerId,
      reason,
    });
    return response.data;
  },

  startProgress: async (id: number): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/start-progress`);
    return response.data;
  },

  requestPending: async (id: number, reason: string): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/pending`, { reason });
    return response.data;
  },

  replyPending: async (id: number, content: string): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/reply-pending`, { content });
    return response.data;
  },

  resolveTicket: async (id: number, payload: ResolveTicketPayload): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/resolve`, payload);
    return response.data;
  },

  updateResolution: async (id: number, resolutionNote: string): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/update-resolution`, {
      resolution_note: resolutionNote,
    });
    return response.data;
  },

  restartInquiry: async (id: number, content: string): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/restart`, { content });
    return response.data;
  },

  closeTicket: async (id: number, reason?: string): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/close`, { reason });
    return response.data;
  },

  cancelTicket: async (id: number, reason?: string): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/cancel`, { reason });
    return response.data;
  },

  submitRating: async (id: number, rating: number, comment?: string): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/rate`, {
      rating,
      comment,
    });
    return response.data;
  },

  toggleFaq: async (id: number): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/toggle-faq`);
    return response.data;
  },
};
