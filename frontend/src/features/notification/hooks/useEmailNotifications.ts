import { useCallback, useEffect, useMemo, useState } from 'react';
import { apiClient } from '../../../api/client';
import { EmailNotificationItem } from '../../ticket/types/ticket';

const MAX_STORED_READ_IDS = 500;
const POLL_INTERVAL_MS = 60000;

const loadReadIds = (key: string): string[] => {
  try {
    const parsed = JSON.parse(localStorage.getItem(key) || '[]');
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

export const useEmailNotifications = (uid?: number) => {
  const storageKey = `helpdesk_read_emails_${uid ?? 'anon'}`;
  const [items, setItems] = useState<EmailNotificationItem[]>([]);
  const [readIds, setReadIds] = useState<string[]>(() => loadReadIds(storageKey));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setReadIds(loadReadIds(storageKey));
  }, [storageKey]);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/tickets/notifications', { params: { limit: 50 } });
      setItems(res.data.data || []);
      setError(null);
    } catch {
      setError('이메일 알림 내역을 불러오지 못했습니다.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, POLL_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [refresh]);

  const persist = useCallback(
    (ids: string[]) => {
      const trimmed = ids.slice(-MAX_STORED_READ_IDS);
      localStorage.setItem(storageKey, JSON.stringify(trimmed));
      setReadIds(trimmed);
    },
    [storageKey]
  );

  const readSet = useMemo(() => new Set(readIds), [readIds]);
  const isRead = useCallback((id: string) => readSet.has(id), [readSet]);

  const markRead = useCallback(
    (id: string) => {
      if (!readSet.has(id)) persist([...readIds, id]);
    },
    [readSet, readIds, persist]
  );

  const markAllRead = useCallback(() => {
    persist(Array.from(new Set([...readIds, ...items.map((i) => i.id)])));
  }, [readIds, items, persist]);

  const unreadCount = useMemo(() => items.filter((i) => !readSet.has(i.id)).length, [items, readSet]);

  return { items, loading, error, refresh, isRead, markRead, markAllRead, unreadCount };
};
