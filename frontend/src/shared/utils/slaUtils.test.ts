import { describe, it, expect } from 'vitest';
import { formatPausedDuration, formatSlaRemaining } from './slaUtils';

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

  it('답변 대기(paused) 상태이면 마감이 과거여도 일시정지 배지를 반환하고 초과로 표시하지 않는다', () => {
    const past = new Date(Date.now() - 2 * 3600 * 1000).toISOString();
    const resByState = formatSlaRemaining(past, true, 'in_progress', '3', 'paused');
    expect(resByState).not.toBeNull();
    expect(resByState?.isPaused).toBe(true);
    expect(resByState?.isOverdue).toBe(false);
    expect(resByState?.isImminent).toBe(false);
    expect(resByState?.text).toBe('SLA 일시정지 (답변 대기)');
    expect(resByState?.badgeClass).toContain('bg-slate-100');

    const resByStatus = formatSlaRemaining(past, false, 'pending', '2');
    expect(resByStatus?.isPaused).toBe(true);
    expect(resByStatus?.isOverdue).toBe(false);
  });

  it('일시정지(paused) 상태라도 해결/종결/취소이면 null을 반환한다', () => {
    const future = new Date(Date.now() + 3600 * 1000).toISOString();
    expect(formatSlaRemaining(future, false, 'resolved', '1', 'paused')).toBeNull();
    expect(formatSlaRemaining(future, false, 'closed', '1', 'paused')).toBeNull();
    expect(formatSlaRemaining(future, false, 'canceled', '1', 'paused')).toBeNull();
  });
});

describe('formatPausedDuration (일시정지 누적 시간 포맷)', () => {
  it('0 이하의 값은 빈 문자열을 반환한다', () => {
    expect(formatPausedDuration(0)).toBe('');
    expect(formatPausedDuration(-10)).toBe('');
  });

  it('3600초 미만은 분 단위로 반환한다', () => {
    expect(formatPausedDuration(59)).toBe('0분');
    expect(formatPausedDuration(60)).toBe('1분');
    expect(formatPausedDuration(1800)).toBe('30분');
  });

  it('3600초 이상은 시간과 분 단위로 반환한다', () => {
    expect(formatPausedDuration(3600)).toBe('1시간 0분');
    expect(formatPausedDuration(5400)).toBe('1시간 30분');
    expect(formatPausedDuration(7320)).toBe('2시간 2분');
  });
});
