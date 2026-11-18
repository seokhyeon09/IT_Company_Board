export type SlaReportUnit = 'week' | 'month';

export type SlaReportPresetKey = '4w' | '12w' | '6m' | '1y';

export interface SlaReportQueryParams {
  date_from?: string;
  date_to?: string;
  unit?: SlaReportUnit;
  category?: string;
}

export interface SlaReportRange {
  date_from: string;
  date_to: string;
  unit: SlaReportUnit;
  category: string | null;
}

export interface SlaReportSummary {
  created: number;
  resolved: number;
  on_time: number;
  breached: number;
  on_time_rate: number | null;
  avg_resolution_hours: number | null;
  open_now: number;
  overdue_now: number;
  paused_now: number;
  avg_paused_hours: number | null;
}

export interface SlaReportSeriesItem {
  period: string;
  created: number;
  resolved: number;
  on_time: number;
  breached: number;
  on_time_rate: number | null;
  avg_resolution_hours: number | null;
}

export interface SlaReportCategoryItem {
  category: string;
  label: string;
  created: number;
  resolved: number;
  on_time_rate: number | null;
  avg_resolution_hours: number | null;
}

export interface SlaReportPriorityItem {
  priority: string;
  label: string;
  created: number;
  resolved: number;
  on_time_rate: number | null;
  avg_resolution_hours: number | null;
}

export interface SlaReportData {
  range: SlaReportRange;
  summary: SlaReportSummary;
  series: SlaReportSeriesItem[];
  by_category: SlaReportCategoryItem[];
  by_priority: SlaReportPriorityItem[];
}

export interface SlaChartPoint {
  period: string;
  label: string;
  created: number;
  resolved: number;
  createdHeightPct: number;
  resolvedHeightPct: number;
  onTimeRate: number | null;
  onTimeRateLabel: string;
}

export const SLA_REPORT_PRESETS: ReadonlyArray<{ key: SlaReportPresetKey; label: string }> = [
  { key: '4w', label: '최근 4주' },
  { key: '12w', label: '최근 12주' },
  { key: '6m', label: '최근 6개월' },
  { key: '1y', label: '최근 1년' },
];

export const SLA_CATEGORY_OPTIONS: ReadonlyArray<{ value: string; label: string }> = [
  { value: '', label: '전체 분야' },
  { value: 'hw', label: '하드웨어' },
  { value: 'sw', label: '소프트웨어' },
  { value: 'network', label: '네트워크' },
  { value: 'account', label: '계정/권한' },
  { value: 'etc', label: '기타' },
];
