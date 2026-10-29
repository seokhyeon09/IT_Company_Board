import { describe, it, expect } from 'vitest';
import { formatResolutionHours } from './durationUtils';

describe('formatResolutionHours (MTTR 시간 포맷 유틸)', () => {
  it('측정 건수가 0이거나 시간이 0 이하이면 기본 안내 문구를 반환한다', () => {
    expect(formatResolutionHours(0, 0)).toBe('집계 데이터 없음');
    expect(formatResolutionHours(undefined, undefined, '-')).toBe('-');
  });

  it('1시간 미만은 분 단위로 변환한다', () => {
    expect(formatResolutionHours(0.5, 2)).toBe('30분');
  });

  it('1시간 이상 24시간 미만은 시간 단위로 표시한다', () => {
    expect(formatResolutionHours(2.4, 3)).toBe('2.4시간');
    expect(formatResolutionHours(3.0, 1)).toBe('3시간');
  });

  it('24시간 이상은 일 + 시간 단위로 표시한다', () => {
    expect(formatResolutionHours(28.5, 4)).toBe('1일 4.5시간');
    expect(formatResolutionHours(48.0, 2)).toBe('2일');
  });
});
