import { describe, it, expect } from 'vitest';
import {
  buildSlaChartPoints,
  calcBarHeightPercent,
  formatOnTimeRate,
  formatPeriodLabel,
  formatReportHours,
  getPresetRange,
} from './slaReport';

describe('slaReport 순수 유틸', () => {
  it('프리셋별 날짜 범위와 집계 단위를 KST 기준으로 결정적으로 계산한다', () => {
    // 2026-11-18T16:00:00Z -> KST 2026-11-19
    const baseUtc = new Date('2026-11-18T16:00:00Z');
    expect(getPresetRange('4w', baseUtc)).toEqual({
      date_from: '2026-10-23',
      date_to: '2026-11-19',
      unit: 'week',
    });
    expect(getPresetRange('12w', baseUtc)).toEqual({
      date_from: '2026-08-28',
      date_to: '2026-11-19',
      unit: 'week',
    });
    expect(getPresetRange('6m', baseUtc)).toEqual({
      date_from: '2026-06-01',
      date_to: '2026-11-19',
      unit: 'month',
    });
    expect(getPresetRange('1y', baseUtc)).toEqual({
      date_from: '2025-12-01',
      date_to: '2026-11-19',
      unit: 'month',
    });
  });

  it('준수율과 평균 해결시간을 포맷한다', () => {
    expect(formatOnTimeRate(87.5)).toBe('87.5%');
    expect(formatOnTimeRate(100)).toBe('100%');
    expect(formatOnTimeRate(null)).toBe('-');
    expect(formatOnTimeRate(undefined)).toBe('-');

    expect(formatReportHours(3.2)).toBe('3.2시간');
    expect(formatReportHours(0)).toBe('0시간');
    expect(formatReportHours(null)).toBe('-');
  });

  it('차트 막대 높이를 최댓값 0, 일부 0, 최소 가시 높이에 맞춰 계산한다', () => {
    expect(calcBarHeightPercent(0, 0)).toBe(0);
    expect(calcBarHeightPercent(0, 10)).toBe(0);
    expect(calcBarHeightPercent(1, 100, 8)).toBe(8);
    expect(calcBarHeightPercent(50, 100, 8)).toBe(50);
    expect(calcBarHeightPercent(100, 100, 8)).toBe(100);

    const points = buildSlaChartPoints(
      [
        {
          period: '2026-11-09',
          created: 0,
          resolved: 0,
          on_time: 0,
          breached: 0,
          on_time_rate: null,
          avg_resolution_hours: null,
        },
        {
          period: '2026-11-16',
          created: 20,
          resolved: 1,
          on_time: 1,
          breached: 0,
          on_time_rate: 100,
          avg_resolution_hours: 1.5,
        },
      ],
      'week'
    );
    expect(points[0].createdHeightPct).toBe(0);
    expect(points[0].onTimeRateLabel).toBe('-');
    expect(points[1].label).toBe('11/16 주');
    expect(points[1].createdHeightPct).toBe(100);
    expect(points[1].resolvedHeightPct).toBe(8);
  });

  it('기간 라벨을 주/월 단위에 맞게 포맷한다', () => {
    expect(formatPeriodLabel('2026-11-16', 'week')).toBe('11/16 주');
    expect(formatPeriodLabel('2026-11-01', 'month')).toBe('2026-11');
  });
});
