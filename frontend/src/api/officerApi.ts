import { apiClient } from './client';
import {
  AbsenceOpenTicket,
  OfficerAbsence,
  OfficerAbsenceInput,
  OfficerAbsenceSaveResult,
} from '../features/dashboard/types/officer';

interface WrappedAbsenceResponse {
  status?: string;
  data?: OfficerAbsence;
  open_tickets?: AbsenceOpenTicket[];
  open_ticket_total?: number;
}

function unwrapAbsence(body: WrappedAbsenceResponse | OfficerAbsence): OfficerAbsence {
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
    const response = await apiClient.get<WrappedAbsenceResponse | OfficerAbsence>(
      '/officers/me/absence'
    );
    return unwrapAbsence(response.data);
  },

  setAbsence: async (payload: OfficerAbsenceInput): Promise<OfficerAbsenceSaveResult> => {
    const normalized: OfficerAbsenceInput = {
      is_absent: payload.is_absent,
      absent_until: payload.is_absent ? payload.absent_until || null : null,
    };
    const response = await apiClient.put<WrappedAbsenceResponse | OfficerAbsence>(
      '/officers/me/absence',
      normalized
    );
    const body = response.data as WrappedAbsenceResponse;
    const openTickets = Array.isArray(body?.open_tickets) ? body.open_tickets : [];
    const openTicketTotal =
      typeof body?.open_ticket_total === 'number' ? body.open_ticket_total : openTickets.length;
    return {
      absence: unwrapAbsence(body),
      openTickets,
      openTicketTotal,
    };
  },
};
