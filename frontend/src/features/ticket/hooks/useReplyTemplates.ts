import { useState, useEffect, useCallback } from 'react';
import { replyTemplateApi } from '../../../api/replyTemplateApi';
import { getErrorMessage } from '../../../api/client';
import { ReplyTemplate, ReplyTemplateInput } from '../types/replyTemplate';

export function useReplyTemplates(category: string) {
  const [templates, setTemplates] = useState<ReplyTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState('');

  const reload = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const list = await replyTemplateApi.list(category || undefined);
      setTemplates(list);
    } catch (err) {
      setError(getErrorMessage(err, '상용구 목록을 불러오지 못했습니다.'));
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => {
    let active = true;
    const loadInitial = async () => {
      setLoading(true);
      setError('');
      try {
        const list = await replyTemplateApi.list(category || undefined);
        if (active) setTemplates(list);
      } catch (err) {
        if (active) setError(getErrorMessage(err, '상용구 목록을 불러오지 못했습니다.'));
      } finally {
        if (active) setLoading(false);
      }
    };
    loadInitial();
    return () => {
      active = false;
    };
  }, [category]);

  const save = useCallback(
    async (input: ReplyTemplateInput): Promise<boolean> => {
      setSaving(true);
      setError('');
      try {
        await replyTemplateApi.create(input);
        await reload();
        return true;
      } catch (err) {
        setError(getErrorMessage(err, '상용구 저장에 실패했습니다.'));
        return false;
      } finally {
        setSaving(false);
      }
    },
    [reload]
  );

  const remove = useCallback(
    async (id: number): Promise<boolean> => {
      setDeletingId(id);
      setError('');
      try {
        await replyTemplateApi.remove(id);
        await reload();
        return true;
      } catch (err) {
        setError(getErrorMessage(err, '상용구 삭제에 실패했습니다.'));
        return false;
      } finally {
        setDeletingId(null);
      }
    },
    [reload]
  );

  const clearError = useCallback(() => setError(''), []);

  return {
    templates,
    loading,
    saving,
    deletingId,
    error,
    clearError,
    save,
    remove,
  };
}
