import {
  SlaChartPoint,
  SlaReportPresetKey,
  SlaReportSeriesItem,
  SlaReportUnit,
} from '../types/slaReport';

const KST_OFFSET_MS = 9 * 60 * 60 * 1000;

function toKstDateParts(baseDate: Date): { year: number; month: number; day: number } {
  const kst = new Date(baseDate.getTime() + KST_OFFSET_MS);
  return {
    year: kst.getUTCFullYear(),
    month: kst.getUTCMonth() + 1,
    day: kst.getUTCDate(),
  };
}

function formatYmd(year: number, month: number, day: number): string {
  const y = String(year).padStart(4, '0');
  const m = String(month).padStart(2, '0');
  const d = String(day).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function addDaysYmd(year: number, month: number, day: number, deltaDays: number): string {
  const dt = new Date(Date.UTC(year, month - 1, day + deltaDays));
  return formatYmd(dt.getUTCFullYear(), dt.getUTCMonth() + 1, dt.getUTCDate());
}

function firstDayMonthsAgo(year: number, month: number, monthsAgo: number): string {
  const totalMonths = year * 12 + (month - 1) - monthsAgo;
  const targetYear = Math.floor(totalMonths / 12);
  const targetMonth = (totalMonths % 12) + 1;
  return formatYmd(targetYear, targetMonth, 1);
}

/**
 * 기준 시각을 KST(UTC+9) 일자 문자열(YYYY-MM-DD)로 변환한다.
 */
export function formatKstDateString(baseDate: Date = new Date()): string {
  const { year, month, day } = toKstDateParts(baseDate);
  return formatYmd(year, month, day);
}

/**
 * 기준 시각을 KST YYYYMMDD 문자열로 변환한다.
 */
export function formatKstCompactDate(baseDate: Date = new Date()): string {
  return formatKstDateString(baseDate).replace(/-/g, '');
}

/**
 * 프리셋 키와 기준 시각으로 조회 범위(date_from, date_to, unit)를 결정적으로 계산한다.
 */
export function getPresetRange(
  preset: SlaReportPresetKey,
  baseDate: Date = new Date()
): { date_from: string; date_to: string; unit: SlaReportUnit } {
  const { year, month, day } = toKstDateParts(baseDate);
  const dateTo = formatYmd(year, month, day);

  switch (preset) {
    case '4w':
      return { date_from: addDaysYmd(year, month, day, -27), date_to: dateTo, unit: 'week' };
    case '12w':
      return { date_from: addDaysYmd(year, month, day, -83), date_to: dateTo, unit: 'week' };
    case '6m':
      return { date_from: firstDayMonthsAgo(year, month, 5), date_to: dateTo, unit: 'month' };
    case '1y':
      return { date_from: firstDayMonthsAgo(year, month, 11), date_to: dateTo, unit: 'month' };
  }
}

export function formatOnTimeRate(rate?: number | null): string {
  if (rate === null || rate === undefined || Number.isNaN(rate)) {
    return '-';
  }
  return `${Number(rate.toFixed(1))}%`;
}

export function formatReportHours(hours?: number | null): string {
  if (hours === null || hours === undefined || Number.isNaN(hours)) {
    return '-';
  }
  return `${Number(hours.toFixed(1))}시간`;
}

export function formatPeriodLabel(period: string, unit: SlaReportUnit): string {
  if (unit === 'month') {
    return period.slice(0, 7);
  }
  const parts = period.split('-');
  if (parts.length === 3) {
    return `${parts[1]}/${parts[2]} 주`;
  }
  return period;
}

export function calcBarHeightPercent(value: number, maxValue: number, minVisiblePercent: number = 8): number {
  if (value <= 0 || maxValue <= 0) {
    return 0;
  }
  return Math.min(100, Math.max(minVisiblePercent, Math.round((value / maxValue) * 100)));
}

export function buildSlaChartPoints(
  series: SlaReportSeriesItem[],
  unit: SlaReportUnit
): SlaChartPoint[] {
  const maxVal = series.reduce((acc, item) => Math.max(acc, item.created, item.resolved), 0);
  return series.map((item) => ({
    period: item.period,
    label: formatPeriodLabel(item.period, unit),
    created: item.created,
    resolved: item.resolved,
    createdHeightPct: calcBarHeightPercent(item.created, maxVal),
    resolvedHeightPct: calcBarHeightPercent(item.resolved, maxVal),
    onTimeRate: item.on_time_rate,
    onTimeRateLabel: formatOnTimeRate(item.on_time_rate),
  }));
}
