import { useState, useEffect, useCallback } from 'react';
import { BulkTicketItemResult } from '../types/bulk';
import {
  MAX_BULK_SELECTION,
  areAllPageTicketsSelected,
  deselectPageTickets,
  removeSucceededIds,
  selectPageTickets,
  toggleSelection,
} from '../utils/selection';

export function useTicketSelection(resetKey: string) {
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [limitWarning, setLimitWarning] = useState('');

  useEffect(() => {
    setSelectedIds([]);
    setLimitWarning('');
  }, [resetKey]);

  const toggleTicket = useCallback((ticketId: number) => {
    setSelectedIds((prev) => {
      const next = toggleSelection(prev, ticketId, MAX_BULK_SELECTION);
      setLimitWarning(
        next.limitReached ? `한 번에 최대 ${MAX_BULK_SELECTION}건까지 선택할 수 있습니다.` : ''
      );
      return next.ids;
    });
  }, []);

  const togglePageAll = useCallback((pageTicketIds: number[]) => {
    setSelectedIds((prev) => {
      if (areAllPageTicketsSelected(prev, pageTicketIds)) {
        setLimitWarning('');
        return deselectPageTickets(prev, pageTicketIds);
      }
      const next = selectPageTickets(prev, pageTicketIds, MAX_BULK_SELECTION);
      setLimitWarning(
        next.limitReached ? `한 번에 최대 ${MAX_BULK_SELECTION}건까지 선택할 수 있습니다.` : ''
      );
      return next.ids;
    });
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedIds([]);
    setLimitWarning('');
  }, []);

  const keepFailedOnly = useCallback((results: BulkTicketItemResult[]) => {
    setSelectedIds((prev) => removeSucceededIds(prev, results));
    setLimitWarning('');
  }, []);

  return {
    selectedIds,
    limitWarning,
    toggleTicket,
    togglePageAll,
    clearSelection,
    keepFailedOnly,
  };
}
