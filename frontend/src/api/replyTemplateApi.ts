import { apiClient } from './client';
import { ReplyTemplate, ReplyTemplateInput } from '../features/ticket/types/replyTemplate';

interface WrappedResponse<T> {
  status?: string;
  data?: T;
}

export const replyTemplateApi = {
  list: async (category?: string): Promise<ReplyTemplate[]> => {
    const response = await apiClient.get<WrappedResponse<ReplyTemplate[]> | ReplyTemplate[]>(
      '/reply-templates',
      { params: category ? { category } : undefined }
    );
    const body = response.data;
    if (Array.isArray(body)) return body;
    return Array.isArray(body?.data) ? body.data : [];
  },

  create: async (payload: ReplyTemplateInput): Promise<ReplyTemplate> => {
    const response = await apiClient.post<WrappedResponse<ReplyTemplate> | ReplyTemplate>(
      '/reply-templates',
      payload
    );
    const body = response.data;
    if (body && typeof body === 'object' && 'data' in body && body.data) {
      return body.data;
    }
    return body as ReplyTemplate;
  },

  update: async (id: number, payload: ReplyTemplateInput): Promise<ReplyTemplate> => {
    const response = await apiClient.put<WrappedResponse<ReplyTemplate> | ReplyTemplate>(
      `/reply-templates/${id}`,
      payload
    );
    const body = response.data;
    if (body && typeof body === 'object' && 'data' in body && body.data) {
      return body.data;
    }
    return body as ReplyTemplate;
  },

  remove: async (id: number): Promise<void> => {
    await apiClient.delete(`/reply-templates/${id}`);
  },
};
