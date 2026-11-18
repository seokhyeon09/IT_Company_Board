import { apiClient } from './client';
import { InternalNote } from '../features/ticket/types/ticket';

interface WrappedResponse<T> {
  status?: string;
  data?: T;
}

export const noteApi = {
  addNote: async (ticketId: number, content: string): Promise<InternalNote> => {
    const response = await apiClient.post<WrappedResponse<InternalNote> | InternalNote>(
      `/tickets/${ticketId}/notes`,
      { content }
    );
    const body = response.data;
    if (body && typeof body === 'object' && 'data' in body && body.data) {
      return body.data;
    }
    return body as InternalNote;
  },
};
