import { useCallback, useEffect, useRef } from 'react';

const DEFAULT_STALE_MS = 60_000;

/**
 * 브라우저 탭 복귀(visibilitychange) 시 마지막 갱신 후 일정 시간(기본 60초)이 지났으면 새로고침을 실행한다.
 */
export function useRefreshOnFocus(
  onRefresh: () => void,
  staleMs: number = DEFAULT_STALE_MS
) {
  const lastRefreshedAtRef = useRef<number>(Date.now());
  const onRefreshRef = useRef(onRefresh);
  onRefreshRef.current = onRefresh;

  const markRefreshed = useCallback(() => {
    lastRefreshedAtRef.current = Date.now();
  }, []);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState !== 'visible') return;
      if (Date.now() - lastRefreshedAtRef.current >= staleMs) {
        lastRefreshedAtRef.current = Date.now();
        onRefreshRef.current();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [staleMs]);

  return { markRefreshed };
}
