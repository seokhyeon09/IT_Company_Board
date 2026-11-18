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
  priority?: string;
  content?: string;
}

export interface AttachmentUploadPayload {
  name: string;
  datas: string;
  mimetype?: string;
}

export const ticketApi = {
  getTickets: async (params: TicketListQueryParams, options?: { signal?: AbortSignal }): Promise<TicketListResponse> => {
    const queryParams: Record<string, any> = {
      offset: params.offset,
      limit: params.limit,
    };
    if (params.status) queryParams.status = params.status;
    if (params.category) queryParams.category = params.category;
    if (params.priority) queryParams.priority = params.priority;
    if (params.search) queryParams.search = params.search;
    if (params.is_overdue) queryParams.is_overdue = true;
    if (params.assigned_to_me) queryParams.assigned_to_me = true;
    if (params.sort_by) queryParams.sort_by = params.sort_by;
    if (params.is_faq) queryParams.is_faq = true;

    const response = await apiClient.get<TicketListResponse>('/tickets', { params: queryParams, ...options });
    return response.data;
  },

  getStats: async (): Promise<TicketStats> => {
    const response = await apiClient.get<any>('/tickets/stats');
    return (response.data as any)?.data || response.data;
  },

  getTicketDetail: async (id: number): Promise<TicketDetail> => {
    const response = await apiClient.get<any>(`/tickets/${id}`);
    return (response.data as any)?.data || response.data;
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
    const response = await apiClient.get<any>('/tickets/officer-stats');
    return (response.data as any)?.data || response.data;
  },

  getOfficers: async (): Promise<{ officers: OfficerSimpleItem[] }> => {
    const response = await apiClient.get<any>('/tickets/officers');
    const d = response.data;
    const list: OfficerSimpleItem[] = Array.isArray(d)
      ? d
      : Array.isArray(d?.data)
      ? d.data
      : Array.isArray(d?.officers)
      ? d.officers
      : [];
    return { officers: list };
  },
};
