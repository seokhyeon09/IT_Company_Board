import { BulkTicketItemResult } from '../types/bulk';

export const MAX_BULK_SELECTION = 50;

export interface SelectionUpdate {
  ids: number[];
  limitReached: boolean;
}

export function toggleSelection(
  selectedIds: number[],
  ticketId: number,
  max: number = MAX_BULK_SELECTION
): SelectionUpdate {
  if (selectedIds.includes(ticketId)) {
    return {
      ids: selectedIds.filter((id) => id !== ticketId),
      limitReached: false,
    };
  }
  if (selectedIds.length >= max) {
    return { ids: selectedIds, limitReached: true };
  }
  return {
    ids: [...selectedIds, ticketId],
    limitReached: false,
  };
}

export function selectPageTickets(
  selectedIds: number[],
  pageTicketIds: number[],
  max: number = MAX_BULK_SELECTION
): SelectionUpdate {
  const next = [...selectedIds];
  const existing = new Set(selectedIds);
  let limitReached = false;

  for (const id of pageTicketIds) {
    if (existing.has(id)) continue;
    if (next.length >= max) {
      limitReached = true;
      break;
    }
    next.push(id);
    existing.add(id);
  }

  return { ids: next, limitReached };
}

export function deselectPageTickets(selectedIds: number[], pageTicketIds: number[]): number[] {
  const pageSet = new Set(pageTicketIds);
  return selectedIds.filter((id) => !pageSet.has(id));
}

export function areAllPageTicketsSelected(selectedIds: number[], pageTicketIds: number[]): boolean {
  if (pageTicketIds.length === 0) return false;
  const selectedSet = new Set(selectedIds);
  return pageTicketIds.every((id) => selectedSet.has(id));
}

export function removeSucceededIds(
  selectedIds: number[],
  results: BulkTicketItemResult[]
): number[] {
  const succeeded = new Set(results.filter((r) => r.ok).map((r) => r.id));
  return selectedIds.filter((id) => !succeeded.has(id));
}
