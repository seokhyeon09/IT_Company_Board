import { useState, useEffect, useCallback } from 'react';
import { officerApi } from '../../../api/officerApi';
import { bulkApi } from '../../../api/bulkApi';
import { ticketApi } from '../../../api/ticketApi';
import { getErrorMessage } from '../../../api/client';
import { OfficerSimpleItem } from '../../ticket/types/ticket';
import {
  AbsenceOpenTicket,
  OfficerAbsence,
  OfficerAbsenceInput,
  OfficerAbsenceSaveResult,
} from '../types/officer';
import { BulkActionResult } from '../types/bulk';
import { aggregateBulkResults, buildBulkPayload, chunkIds } from '../utils/bulkResult';
import { isValidAbsenceUntil, todayIsoDate } from '../../../shared/utils/absenceUtils';

const ABSENCE_REASSIGN_REASON = '담당자 부재로 인한 인계';

export function useOfficerAbsence(onTicketsChanged?: () => void) {
  const [absence, setAbsence] = useState<OfficerAbsence>({
    is_absent: false,
    absent_until: null,
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [openTickets, setOpenTickets] = useState<AbsenceOpenTicket[]>([]);
  const [openTicketTotal, setOpenTicketTotal] = useState(0);
  const [officers, setOfficers] = useState<OfficerSimpleItem[]>([]);
  const [reassigning, setReassigning] = useState(false);
  const [reassignError, setReassignError] = useState('');
  const [reassignResult, setReassignResult] = useState<BulkActionResult | null>(null);

  useEffect(() => {
    let active = true;
    const loadAbsence = async () => {
      setLoading(true);
      try {
        const data = await officerApi.getAbsence();
        if (active) setAbsence(data);
      } catch (err) {
        console.error('Failed to load officer absence:', err);
      } finally {
        if (active) setLoading(false);
      }
    };
    loadAbsence();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (openTickets.length === 0) return;
    let active = true;
    ticketApi
      .getOfficers()
      .then((res) => {
        if (active) setOfficers(res.officers || []);
      })
      .catch(() => {
        if (active) setOfficers([]);
      });
    return () => {
      active = false;
    };
  }, [openTickets.length]);

  const saveAbsence = useCallback(
    async (input: OfficerAbsenceInput): Promise<OfficerAbsenceSaveResult | null> => {
      const until = input.is_absent ? input.absent_until || null : null;
      if (input.is_absent && until && !isValidAbsenceUntil(until, todayIsoDate())) {
        setError('종료일은 오늘 이후 날짜만 선택할 수 있습니다.');
        return null;
      }

      setSaving(true);
      setError('');
      setReassignError('');
      setReassignResult(null);
      try {
        const res = await officerApi.setAbsence({
          is_absent: input.is_absent,
          absent_until: until,
        });
        setAbsence(res.absence);
        setOpenTickets(res.openTickets);
        setOpenTicketTotal(res.openTicketTotal);
        return res;
      } catch (err) {
        setError(getErrorMessage(err, '부재 설정 저장에 실패했습니다.'));
        return null;
      } finally {
        setSaving(false);
      }
    },
    []
  );

  const reassignOpenTickets = useCallback(
    async (mode: 'assign_auto' | 'assign', officerId?: number | '') => {
      if (openTickets.length === 0) return;
      if (mode === 'assign' && !officerId) {
        setReassignError('인계할 담당자를 선택해 주세요.');
        return;
      }
      setReassigning(true);
      setReassignError('');
      try {
        const chunks = chunkIds(
          openTickets.map((t) => t.id),
          50
        );
        const batchResults: BulkActionResult[] = [];
        for (const batchIds of chunks) {
          const payload = buildBulkPayload({
            ticketIds: batchIds,
            action: mode,
            officerId,
            reason: ABSENCE_REASSIGN_REASON,
          });
          batchResults.push(await bulkApi.executeBulk(payload));
        }
        const combined = aggregateBulkResults(mode, batchResults);
        setReassignResult(combined);
        onTicketsChanged?.();
      } catch (err) {
        setReassignError(getErrorMessage(err, '부재 연계 인계 처리에 실패했습니다.'));
      } finally {
        setReassigning(false);
      }
    },
    [openTickets, onTicketsChanged]
  );

  const dismissReassignPanel = useCallback(() => {
    setOpenTickets([]);
    setOpenTicketTotal(0);
    setReassignResult(null);
    setReassignError('');
  }, []);

  const clearError = useCallback(() => setError(''), []);

  return {
    absence,
    loading,
    saving,
    error,
    openTickets,
    openTicketTotal,
    officers,
    reassigning,
    reassignError,
    reassignResult,
    clearError,
    saveAbsence,
    reassignOpenTickets,
    dismissReassignPanel,
  };
}
