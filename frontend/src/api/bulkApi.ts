import { apiClient } from './client';
import { BulkActionPayload, BulkActionResult } from '../features/dashboard/types/bulk';

interface WrappedResponse<T> {
  status?: string;
  data?: T;
}

export const bulkApi = {
  executeBulk: async (payload: BulkActionPayload): Promise<BulkActionResult> => {
    const response = await apiClient.post<WrappedResponse<BulkActionResult> | BulkActionResult>(
      '/tickets/bulk',
      payload
    );
    const body = response.data;
    if (body && typeof body === 'object' && 'data' in body && body.data) {
      return body.data;
    }
    return body as BulkActionResult;
  },
};
