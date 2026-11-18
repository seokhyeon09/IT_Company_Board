import React from 'react';
import { TrendingUp } from 'lucide-react';
import { SlaReportSeriesItem, SlaReportUnit } from '../types/slaReport';
import { buildSlaChartPoints } from '../utils/slaReport';

interface SlaReportTrendChartProps {
  series: SlaReportSeriesItem[];
  unit: SlaReportUnit;
}

export const SlaReportTrendChart: React.FC<SlaReportTrendChartProps> = ({ series, unit }) => {
  const points = buildSlaChartPoints(series, unit);

  return (
    <div className="border border-slate-200 rounded-xl p-4 bg-white">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <h4 className="text-xs font-bold text-slate-700 flex items-center">
          <TrendingUp className="w-4 h-4 mr-1.5 text-indigo-600" /> 기간별 접수/해결 추이 및 SLA 준수율
        </h4>
        <div className="flex items-center gap-3 text-[11px] text-slate-600">
          <span className="inline-flex items-center">
            <span className="w-2.5 h-2.5 rounded-xs bg-indigo-500 mr-1" /> 접수
          </span>
          <span className="inline-flex items-center">
            <span className="w-2.5 h-2.5 rounded-xs bg-emerald-500 mr-1" /> 해결
          </span>
          <span className="inline-flex items-center">
            <span className="w-2.5 h-2.5 rounded-xs bg-teal-500 mr-1" /> 준수율(%)
          </span>
        </div>
      </div>

      {points.length === 0 ? (
        <div className="py-10 text-center text-xs text-slate-400">
          표시할 기간별 데이터가 없습니다.
        </div>
      ) : (
        <div className="overflow-x-auto pb-1">
          <div
            className="flex items-end gap-2 min-w-full"
            style={{ minWidth: `${Math.max(points.length * 64, 480)}px` }}
          >
            {points.map((pt) => {
              const rateWidth = pt.onTimeRate !== null ? Math.max(4, Math.min(100, pt.onTimeRate)) : 0;
              const rateColor =
                pt.onTimeRate === null
                  ? 'bg-slate-200'
                  : pt.onTimeRate >= 90
                  ? 'bg-emerald-500'
                  : pt.onTimeRate >= 70
                  ? 'bg-amber-500'
                  : 'bg-rose-500';

              return (
                <div key={pt.period} className="flex-1 min-w-[56px] flex flex-col items-center">
                  <div className="text-[10px] text-slate-500 font-medium mb-1">
                    {pt.created}/{pt.resolved}
                  </div>
                  <div className="w-full h-32 bg-slate-50 border border-slate-100 rounded-lg px-2 pt-2 pb-1 flex items-end justify-center gap-1.5">
                    <div
                      title={`접수 ${pt.created}건`}
                      className="w-3.5 bg-indigo-500 rounded-t transition-all"
                      style={{ height: `${pt.createdHeightPct}%` }}
                    />
                    <div
                      title={`해결 ${pt.resolved}건`}
                      className="w-3.5 bg-emerald-500 rounded-t transition-all"
                      style={{ height: `${pt.resolvedHeightPct}%` }}
                    />
                  </div>
                  <div className="w-full mt-1.5 px-1">
                    <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${rateColor}`}
                        style={{ width: `${rateWidth}%` }}
                      />
                    </div>
                    <div className="text-[10px] font-semibold text-slate-700 text-center mt-0.5">
                      {pt.onTimeRateLabel}
                    </div>
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5 whitespace-nowrap">
                    {pt.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
