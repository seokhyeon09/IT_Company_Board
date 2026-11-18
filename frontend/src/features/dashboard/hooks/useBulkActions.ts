import { useState, useEffect, useCallback } from 'react';
import { bulkApi } from '../../../api/bulkApi';
import { ticketApi } from '../../../api/ticketApi';
import { getErrorMessage } from '../../../api/client';
import { OfficerSimpleItem } from '../../ticket/types/ticket';
import { BulkActionPayload, BulkActionResult } from '../types/bulk';

interface UseBulkActionsOptions {
  isOfficer: boolean;
  onSuccess?: (result: BulkActionResult) => void;
}

export function useBulkActions({ isOfficer, onSuccess }: UseBulkActionsOptions) {
  const [officers, setOfficers] = useState<OfficerSimpleItem[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<BulkActionResult | null>(null);

  useEffect(() => {
    if (!isOfficer) return;
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
  }, [isOfficer]);

  const executeBulk = useCallback(
    async (payload: BulkActionPayload): Promise<BulkActionResult | null> => {
      setSubmitting(true);
      setError('');
      try {
        const res = await bulkApi.executeBulk(payload);
        setResult(res);
        onSuccess?.(res);
        return res;
      } catch (err) {
        setError(getErrorMessage(err, '일괄 처리에 실패했습니다.'));
        return null;
      } finally {
        setSubmitting(false);
      }
    },
    [onSuccess]
  );

  const clearResult = useCallback(() => {
    setResult(null);
    setError('');
  }, []);

  return {
    officers,
    submitting,
    error,
    result,
    executeBulk,
    clearResult,
  };
}
