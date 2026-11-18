import { describe, it, expect } from 'vitest';
import {
  formatAbsenceLabel,
  formatShortMonthDay,
  todayIsoDate,
  isValidAbsenceUntil,
} from './absenceUtils';

describe('formatAbsenceLabel', () => {
  it('부재 중이 아니면 빈 문자열을 반환한다', () => {
    expect(formatAbsenceLabel({ is_absent: false, absent_until: '2026-12-31' })).toBe('');
    expect(formatAbsenceLabel({ is_absent: undefined, absent_until: null })).toBe('');
  });

  it('기한이 없으면 부재중을 반환한다', () => {
    expect(formatAbsenceLabel({ is_absent: true, absent_until: null })).toBe('부재중');
    expect(formatAbsenceLabel({ is_absent: true, absent_until: '' })).toBe('부재중');
  });

  it('기한이 있으면 부재중 (~M/D) 형식으로 반환한다', () => {
    expect(formatAbsenceLabel({ is_absent: true, absent_until: '2026-03-05' })).toBe('부재중 (~3/5)');
    expect(formatAbsenceLabel({ is_absent: true, absent_until: '2026-12-25' })).toBe('부재중 (~12/25)');
  });
});

describe('formatShortMonthDay', () => {
  it('ISO 날짜에서 앞자리 0을 제거한 M/D를 반환한다', () => {
    expect(formatShortMonthDay('2026-01-09')).toBe('1/9');
    expect(formatShortMonthDay(null)).toBe('');
  });
});

describe('todayIsoDate', () => {
  it('로컬 날짜 기준 YYYY-MM-DD를 반환한다', () => {
    const sample = new Date(2026, 2, 7, 23, 55, 0); // 2026-03-07 local
    expect(todayIsoDate(sample)).toBe('2026-03-07');
  });
});

describe('isValidAbsenceUntil', () => {
  it('빈 값은 허용한다', () => {
    expect(isValidAbsenceUntil('', '2026-11-18')).toBe(true);
    expect(isValidAbsenceUntil(null, '2026-11-18')).toBe(true);
    expect(isValidAbsenceUntil(undefined, '2026-11-18')).toBe(true);
  });

  it('오늘 이상인 날짜만 true를 반환한다', () => {
    expect(isValidAbsenceUntil('2026-11-18', '2026-11-18')).toBe(true);
    expect(isValidAbsenceUntil('2026-11-19', '2026-11-18')).toBe(true);
    expect(isValidAbsenceUntil('2026-11-17', '2026-11-18')).toBe(false);
  });

  it('형식이 잘못되거나 존재하지 않는 날짜는 false를 반환한다', () => {
    expect(isValidAbsenceUntil('2026/11/19', '2026-11-18')).toBe(false);
    expect(isValidAbsenceUntil('2026-02-30', '2026-01-01')).toBe(false);
  });
});
