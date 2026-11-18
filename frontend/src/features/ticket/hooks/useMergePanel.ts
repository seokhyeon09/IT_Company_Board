import { useState, useEffect, useCallback } from 'react';
import { mergeApi } from '../../../api/mergeApi';
import { getErrorMessage } from '../../../api/client';
import { MergeCandidateItem } from '../types/ticket';
import { validateMergeReason } from '../utils/merge';

export function useMergeCandidates(ticketId: number, enabled: boolean) {
  const [candidates, setCandidates] = useState<MergeCandidateItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadCandidates = useCallback(async () => {
    if (!enabled) return;
    setLoading(true);
    setError('');
    try {
      const list = await mergeApi.getCandidates(ticketId);
      setCandidates(list);
    } catch (err) {
      setError(getErrorMessage(err, '병합 후보를 불러오지 못했습니다.'));
    } finally {
      setLoading(false);
    }
  }, [ticketId, enabled]);

  useEffect(() => {
    setCandidates([]);
    setError('');
    if (enabled) {
      loadCandidates();
    }
  }, [enabled, loadCandidates]);

  return { candidates, loading, error, reloadCandidates: loadCandidates };
}

export function useMergeExecution(
  ticketId: number,
  writeDate?: string,
  onMerged?: () => void
) {
  const [selectedTarget, setSelectedTarget] = useState<MergeCandidateItem | null>(null);
  const [reason, setReason] = useState('');
  const [confirming, setConfirming] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setSelectedTarget(null);
    setReason('');
    setConfirming(false);
    setError('');
  }, [ticketId]);

  const requestConfirm = useCallback(() => {
    if (!selectedTarget) {
      setError('병합 대상 문의를 선택해 주세요.');
      return;
    }
    const check = validateMergeReason(reason);
    if (!check.valid) {
      setError(check.error);
      return;
    }
    setError('');
    setConfirming(true);
  }, [selectedTarget, reason]);

  const executeMerge = useCallback(async () => {
    if (!selectedTarget || submitting) return;
    const check = validateMergeReason(reason);
    if (!check.valid) {
      setError(check.error);
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await mergeApi.mergeTicket(ticketId, {
        target_id: selectedTarget.id,
        reason: check.trimmed || undefined,
        if_match_write_date: writeDate,
      });
      setConfirming(false);
      setSelectedTarget(null);
      setReason('');
      onMerged?.();
    } catch (err) {
      setError(getErrorMessage(err, '문의 병합에 실패했습니다.'));
    } finally {
      setSubmitting(false);
    }
  }, [ticketId, writeDate, selectedTarget, reason, submitting, onMerged]);

  return {
    selectedTarget,
    setSelectedTarget: (cand: MergeCandidateItem | null) => {
      setSelectedTarget(cand);
      setConfirming(false);
      setError('');
    },
    reason,
    setReason,
    confirming,
    cancelConfirm: () => setConfirming(false),
    submitting,
    error,
    requestConfirm,
    executeMerge,
  };
}
