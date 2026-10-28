import { apiClient } from './client';
import { Ticket, TicketDetail, Attachment, OfficerSimpleItem } from '../features/ticket/types/ticket';
import { TicketStats, OfficerStatsData, TicketListQueryParams } from '../features/dashboard/types/dashboard';

export interface TicketListResponse {
  total: number;
  tickets: Ticket[];
}

export interface TicketCreatePayload {
  title: string;
  category: string;
  priority?: string;
  content: string;
  attachment_base64?: string;
  attachment_name?: string;
}

export interface TicketUpdatePayload {
  title?: string;
  category?: string;
  content?: string;
}

export interface AttachmentUploadPayload {
  name: string;
  datas: string;
  mimetype?: string;
}

export const ticketApi = {
  getTickets: async (params: TicketListQueryParams): Promise<TicketListResponse> => {
    const queryParams: Record<string, any> = {
      offset: params.offset,
      limit: params.limit,
    };
    if (params.statusFilter) queryParams.status = params.statusFilter;
    if (params.categoryFilter) queryParams.category = params.categoryFilter;
    if (params.priorityFilter) queryParams.priority = params.priorityFilter;
    if (params.searchQuery) queryParams.search = params.searchQuery;
    if (params.isOverdueOnly) queryParams.overdue_only = true;

    const response = await apiClient.get<TicketListResponse>('/tickets', { params: queryParams });
    return response.data;
  },

  getStats: async (): Promise<TicketStats> => {
    const response = await apiClient.get<TicketStats>('/tickets/stats');
    return response.data;
  },

  getTicketDetail: async (id: number): Promise<TicketDetail> => {
    const response = await apiClient.get<TicketDetail>(`/tickets/${id}`);
    return response.data;
  },

  createTicket: async (payload: TicketCreatePayload): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>('/tickets', payload);
    return response.data;
  },

  updateTicket: async (id: number, payload: TicketUpdatePayload): Promise<TicketDetail> => {
    const response = await apiClient.post<TicketDetail>(`/tickets/${id}/update`, payload);
    return response.data;
  },

  uploadAttachment: async (id: number, payload: AttachmentUploadPayload): Promise<Attachment> => {
    const response = await apiClient.post<Attachment>(`/tickets/${id}/attachments`, payload);
    return response.data;
  },

  getAttachment: async (ticketId: number, attachmentId: number): Promise<{ datas: string; name: string; mimetype: string }> => {
    const response = await apiClient.get(`/tickets/${ticketId}/attachments/${attachmentId}`);
    return response.data;
  },

  getOfficerStats: async (): Promise<OfficerStatsData> => {
    const response = await apiClient.get<OfficerStatsData>('/tickets/officer-stats');
    return response.data;
  },

  getOfficers: async (): Promise<{ officers: OfficerSimpleItem[] }> => {
    const response = await apiClient.get<{ officers: OfficerSimpleItem[] }>('/tickets/officers');
    return response.data;
  },
};
