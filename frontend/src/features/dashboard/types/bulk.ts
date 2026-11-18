export type BulkActionType = 'assign' | 'assign_auto' | 'start_progress' | 'close';

export type BulkPanelMode = 'assign' | 'start_progress' | 'close' | null;

export interface BulkActionPayload {
  ticket_ids: number[];
  action: BulkActionType;
  officer_id?: number;
  reason?: string;
  note?: string;
}

export interface BulkTicketItemResult {
  id: number;
  ticket_number: string | null;
  ok: boolean;
  message: string;
}

export interface BulkActionResult {
  action: BulkActionType;
  total: number;
  success_count: number;
  fail_count: number;
  results: BulkTicketItemResult[];
}
