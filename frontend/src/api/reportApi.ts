import { apiClient } from './client';
import { SlaReportData, SlaReportQueryParams } from '../features/dashboard/types/slaReport';
import { formatKstCompactDate } from '../features/dashboard/utils/slaReport';
import { parseContentDispositionFilename } from '../shared/utils/contentDisposition';

interface WrappedReportResponse {
  status?: string;
  data?: SlaReportData;
}

function buildReportQuery(params: SlaReportQueryParams): Record<string, string> {
  const query: Record<string, string> = {};
  if (params.date_from) query.date_from = params.date_from;
  if (params.date_to) query.date_to = params.date_to;
  if (params.unit) query.unit = params.unit;
  if (params.category) query.category = params.category;
  return query;
}

export const reportApi = {
  getSlaReport: async (
    params: SlaReportQueryParams,
    options?: { signal?: AbortSignal }
  ): Promise<SlaReportData> => {
    const response = await apiClient.get<WrappedReportResponse | SlaReportData>('/reports/sla', {
      params: buildReportQuery(params),
      signal: options?.signal,
    });
    const body = response.data;
    if (body && typeof body === 'object' && 'data' in body && body.data) {
      return body.data;
    }
    return body as SlaReportData;
  },

  exportSlaReport: async (
    params: SlaReportQueryParams
  ): Promise<{ blob: Blob; filename: string }> => {
    try {
      const response = await apiClient.get<Blob>('/reports/sla/export', {
        params: buildReportQuery(params),
        responseType: 'blob',
      });
      const headers = response.headers || {};
      const filename =
        parseContentDispositionFilename(headers['content-disposition']) ||
        `sla-report_${formatKstCompactDate()}.csv`;
      return { blob: response.data, filename };
    } catch (err: any) {
      const resData = err?.response?.data;
      if (resData && typeof resData.text === 'function') {
        try {
          const text = await resData.text();
          err.response.data = JSON.parse(text);
        } catch {
          // Keep original error if blob response is not valid JSON
        }
      }
      throw err;
    }
  },
};
