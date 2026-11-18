export interface OfficerAbsence {
  is_absent: boolean;
  absent_until: string | null;
}

export interface OfficerAbsenceInput {
  is_absent: boolean;
  absent_until?: string | null;
}

export interface AbsenceOpenTicket {
  id: number;
  ticket_number: string;
  title: string;
  status: string;
  priority: string;
  category: string;
}

export interface OfficerAbsenceSaveResult {
  absence: OfficerAbsence;
  openTickets: AbsenceOpenTicket[];
  openTicketTotal: number;
}
