import { useState, useEffect, useCallback } from 'react';
import { officerApi } from '../../../api/officerApi';
import { getErrorMessage } from '../../../api/client';
import { OfficerAbsence, OfficerAbsenceInput } from '../types/officer';
import { isValidAbsenceUntil, todayIsoDate } from '../../../shared/utils/absenceUtils';

export function useOfficerAbsence() {
  const [absence, setAbsence] = useState<OfficerAbsence>({
    is_absent: false,
    absent_until: null,
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

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

  const saveAbsence = useCallback(async (input: OfficerAbsenceInput): Promise<boolean> => {
    const until = input.is_absent ? input.absent_until || null : null;
    if (input.is_absent && until && !isValidAbsenceUntil(until, todayIsoDate())) {
      setError('종료일은 오늘 이후 날짜만 선택할 수 있습니다.');
      return false;
    }

    setSaving(true);
    setError('');
    try {
      const updated = await officerApi.setAbsence({
        is_absent: input.is_absent,
        absent_until: until,
      });
      setAbsence(updated);
      return true;
    } catch (err) {
      setError(getErrorMessage(err, '부재 설정 저장에 실패했습니다.'));
      return false;
    } finally {
      setSaving(false);
    }
  }, []);

  const clearError = useCallback(() => setError(''), []);

  return {
    absence,
    loading,
    saving,
    error,
    clearError,
    saveAbsence,
  };
}
