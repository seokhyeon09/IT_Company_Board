import { apiClient } from './client';
import { MergeCandidateItem } from '../features/ticket/types/ticket';

export interface MergeTicketPayload {
  target_id: number;
  reason?: string;
  if_match_write_date?: string;
}

export interface MergeTicketResult {
  id: number;
  ticket_number: string;
  status: string;
  merged_into_id?: number | null;
  merged_into_number?: string | null;
}

interface CandidatesWrappedResponse {
  status?: string;
  data?: {
    candidates?: MergeCandidateItem[];
  };
}

interface MergeWrappedResponse {
  status?: string;
  data?: MergeTicketResult;
}

export const mergeApi = {
  getCandidates: async (ticketId: number, limit = 5): Promise<MergeCandidateItem[]> => {
    const response = await apiClient.get<CandidatesWrappedResponse>(
      `/tickets/${ticketId}/merge-candidates`,
      { params: { limit } }
    );
    return response.data?.data?.candidates ?? [];
  },

  mergeTicket: async (ticketId: number, payload: MergeTicketPayload): Promise<MergeTicketResult> => {
    const response = await apiClient.post<MergeWrappedResponse | MergeTicketResult>(
      `/tickets/${ticketId}/merge`,
      payload
    );
    const body = response.data;
    if (body && typeof body === 'object' && 'data' in body && body.data) {
      return body.data;
    }
    return body as MergeTicketResult;
  },
};
