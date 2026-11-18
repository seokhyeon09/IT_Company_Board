import { useState, useRef, useEffect, useCallback } from 'react';
import { ticketApi } from '../../../api/ticketApi';
import { getErrorMessage } from '../../../api/client';
import { downloadBlob } from '../../../shared/utils/downloadBlob';
import { TicketExportQueryParams } from '../types/dashboard';

export function useTicketExport(exportParams: TicketExportQueryParams) {
  const [exporting, setExporting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => clearTimer();
  }, [clearTimer]);

  const exportCsv = useCallback(async () => {
    if (exporting) return;
    clearTimer();
    setExporting(true);
    setMessage('');
    setError('');

    try {
      const { blob, filename, truncated } = await ticketApi.exportTickets(exportParams);
      downloadBlob(blob, filename);
      setMessage(
        truncated
          ? '조회 결과가 5,000건을 초과하여 상위 5,000건만 CSV로 내보냈습니다.'
          : 'CSV 파일을 다운로드했습니다.'
      );
      timerRef.current = setTimeout(() => {
        setMessage('');
        timerRef.current = null;
      }, 3000);
    } catch (err) {
      setError(getErrorMessage(err, 'CSV 내보내기에 실패했습니다.'));
    } finally {
      setExporting(false);
    }
  }, [exporting, exportParams, clearTimer]);

  return {
    exporting,
    message,
    error,
    exportCsv,
  };
}
