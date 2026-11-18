export interface OfficerAbsence {
  is_absent: boolean;
  absent_until: string | null;
}

export interface OfficerAbsenceInput {
  is_absent: boolean;
  absent_until?: string | null;
}
