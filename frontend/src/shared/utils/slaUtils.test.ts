import { describe, it, expect } from 'vitest';
import { formatSlaRemaining } from './slaUtils';

describe('formatSlaRemaining (SLA 4단계 배지 판정)', () => {
  it('종결/해결/취소 상태이거나 기한이 없으면 null을 반환한다', () => {
    const future = new Date(Date.now() + 3600 * 1000).toISOString();
    expect(formatSlaRemaining(undefined, false, 'submitted')).toBeNull();
    expect(formatSlaRemaining(future, false, 'resolved')).toBeNull();
    expect(formatSlaRemaining(future, false, 'closed')).toBeNull();
    expect(formatSlaRemaining(future, false, 'canceled')).toBeNull();
  });

  it('마감 시각이 지났거나 isOverdue가 true이면 초과(overdue) 배지를 반환한다', () => {
    const past = new Date(Date.now() - 90 * 60 * 1000).toISOString();
    const res = formatSlaRemaining(past, true, 'in_progress', '2');
    expect(res).not.toBeNull();
    expect(res?.isOverdue).toBe(true);
    expect(res?.text).toContain('초과');
    expect(res?.badgeClass).toContain('bg-rose-100');
  });

  it('우선순위별 임계 시간 이하로 남았으면 임박(imminent) 주황색 배지를 반환한다', () => {
    // 긴급('3')은 임계 1시간 -> 30분 남음은 임박
    const in30Min = new Date(Date.now() + 30 * 60 * 1000).toISOString();
    const res = formatSlaRemaining(in30Min, false, 'assigned', '3');
    expect(res).not.toBeNull();
    expect(res?.isOverdue).toBe(false);
    expect(res?.isImminent).toBe(true);
    expect(res?.text).toContain('SLA 임박');
    expect(res?.badgeClass).toContain('bg-amber-100');
  });

  it('서버 slaState가 imminent이면 잔여 시간과 무관하게 임박 배지를 반환한다', () => {
    const in10Hours = new Date(Date.now() + 10 * 3600 * 1000).toISOString();
    const res = formatSlaRemaining(in10Hours, false, 'submitted', '1', 'imminent');
    expect(res?.isImminent).toBe(true);
    expect(res?.text).toContain('SLA 임박');
  });

  it('충분한 여유 시간이 남았으면 정상(ok) 녹색 배지를 반환한다', () => {
    const in24Hours = new Date(Date.now() + 24 * 3600 * 1000).toISOString();
    const res = formatSlaRemaining(in24Hours, false, 'in_progress', '1', 'ok');
    expect(res?.isOverdue).toBe(false);
    expect(res?.isImminent).toBe(false);
    expect(res?.badgeClass).toContain('bg-emerald-50');
  });
});
