import React from 'react';
import { Download, Loader2 } from 'lucide-react';
import {
  SLA_CATEGORY_OPTIONS,
  SLA_REPORT_PRESETS,
  SlaReportPresetKey,
  SlaReportUnit,
} from '../types/slaReport';

interface SlaReportControlsProps {
  preset: SlaReportPresetKey;
  unit: SlaReportUnit;
  category: string;
  exporting: boolean;
  exportError: string | null;
  onSelectPreset: (preset: SlaReportPresetKey) => void;
  onChangeUnit: (unit: SlaReportUnit) => void;
  onChangeCategory: (category: string) => void;
  onExportCsv: () => void;
}

export const SlaReportControls: React.FC<SlaReportControlsProps> = ({
  preset,
  unit,
  category,
  exporting,
  exportError,
  onSelectPreset,
  onChangeUnit,
  onChangeCategory,
  onExportCsv,
}) => {
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2 bg-slate-50 border border-slate-200 rounded-xl p-3">
        <div className="flex flex-wrap items-center gap-1.5">
          {SLA_REPORT_PRESETS.map((item) => {
            const active = preset === item.key;
            return (
              <button
                key={item.key}
                type="button"
                onClick={() => onSelectPreset(item.key)}
                className={`px-2.5 py-1.5 text-xs font-semibold rounded-lg border transition-colors cursor-pointer ${
                  active
                    ? 'bg-indigo-600 text-white border-indigo-600'
                    : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-100'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="inline-flex rounded-lg border border-slate-200 bg-white p-0.5">
            <button
              type="button"
              onClick={() => onChangeUnit('week')}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors cursor-pointer ${
                unit === 'week' ? 'bg-indigo-100 text-indigo-700' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              주 단위
            </button>
            <button
              type="button"
              onClick={() => onChangeUnit('month')}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors cursor-pointer ${
                unit === 'month' ? 'bg-indigo-100 text-indigo-700' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              월 단위
            </button>
          </div>

          <select
            aria-label="분야 필터"
            value={category}
            onChange={(e) => onChangeCategory(e.target.value)}
            className="text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {SLA_CATEGORY_OPTIONS.map((opt) => (
              <option key={opt.value || 'all'} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          <button
            type="button"
            disabled={exporting}
            onClick={onExportCsv}
            className="flex items-center text-xs font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-200 px-3 py-1.5 rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {exporting ? (
              <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin text-slate-500" />
            ) : (
              <Download className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
            )}
            {exporting ? '내보내는 중...' : 'CSV 내보내기'}
          </button>
        </div>
      </div>

      {exportError && (
        <p className="text-xs text-rose-600 font-medium text-right">{exportError}</p>
      )}
    </div>
  );
};
