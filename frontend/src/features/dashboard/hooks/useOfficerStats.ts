import { useState, useEffect } from 'react';
import { ticketApi } from '../../../api/ticketApi';
import { getErrorMessage } from '../../../api/client';
import { OfficerStatsData } from '../types/dashboard';

export function useOfficerStats(isOpen: boolean) {
  const [data, setData] = useState<OfficerStatsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    const fetchOfficerStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await ticketApi.getOfficerStats();
        setData((res as any).data || res);
      } catch (err: any) {
        setError(getErrorMessage(err, '담당자별 통계 정보를 불러오지 못했습니다.'));
      } finally {
        setLoading(false);
      }
    };
    fetchOfficerStats();
  }, [isOpen]);

  return { data, loading, error };
}
