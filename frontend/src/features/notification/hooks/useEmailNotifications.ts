import { useCallback, useEffect, useMemo, useState } from 'react';
import { apiClient } from '../../../api/client';
import { EmailNotificationItem } from '../../ticket/types/ticket';

const POLL_INTERVAL_MS = 60000;

export const useEmailNotifications = (_uid?: number) => {
  const [items, setItems] = useState<EmailNotificationItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const isRead = useCallback(
    (id: string) => {
      const item = items.find((i) => i.id === id);
      return Boolean(item?.is_read);
    },
    [items]
  );

  const markRead = useCallback(
    async (id: string) => {
      const target = items.find((i) => i.id === id);
      if (target && target.is_read) return;

      // 낙관적 UI 업데이트
      setItems((prev) =>
        prev.map((i) => (i.id === id ? { ...i, is_read: true } : i))
      );

      // 서버 DB에 읽음 기록 저장
      try {
        await apiClient.post('/tickets/notifications/read', {
          notification_ids: [id],
        });
      } catch {
        // 백그라운드 저장 실패 시 다음 refresh에서 자동 동기화
      }
    },
    [items]
  );

  const markAllRead = useCallback(async () => {
    const unreadIds = items.filter((i) => !i.is_read).map((i) => i.id);
    if (unreadIds.length === 0) return;

    // 낙관적 UI 업데이트
    setItems((prev) => prev.map((i) => ({ ...i, is_read: true })));

    // 서버 DB에 읽음 기록 저장
    try {
      await apiClient.post('/tickets/notifications/read', {
        notification_ids: unreadIds,
      });
    } catch {
      // 다음 refresh에서 동기화
    }
  }, [items]);

  const unreadCount = useMemo(
    () => items.filter((i) => !i.is_read).length,
    [items]
  );

  return { items, loading, error, refresh, isRead, markRead, markAllRead, unreadCount };
};
