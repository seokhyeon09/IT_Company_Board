import { apiClient } from './client';
import { OfficerAbsence, OfficerAbsenceInput } from '../features/dashboard/types/officer';

interface WrappedResponse<T> {
  status?: string;
  data?: T;
}

function unwrapAbsence(body: WrappedResponse<OfficerAbsence> | OfficerAbsence): OfficerAbsence {
  const raw = body && typeof body === 'object' && 'data' in body && body.data
    ? body.data
    : (body as OfficerAbsence);
  return {
    is_absent: Boolean(raw?.is_absent),
    absent_until: raw?.absent_until ?? null,
  };
}

export const officerApi = {
  getAbsence: async (): Promise<OfficerAbsence> => {
    const response = await apiClient.get<WrappedResponse<OfficerAbsence> | OfficerAbsence>(
      '/officers/me/absence'
    );
    return unwrapAbsence(response.data);
  },

  setAbsence: async (payload: OfficerAbsenceInput): Promise<OfficerAbsence> => {
    const normalized: OfficerAbsenceInput = {
      is_absent: payload.is_absent,
      absent_until: payload.is_absent ? payload.absent_until || null : null,
    };
    const response = await apiClient.put<WrappedResponse<OfficerAbsence> | OfficerAbsence>(
      '/officers/me/absence',
      normalized
    );
    return unwrapAbsence(response.data);
  },
};
