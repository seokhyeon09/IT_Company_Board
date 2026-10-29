import React from 'react';
import { Timer, Layers } from 'lucide-react';
import { CategoryStatItem } from '../types/dashboard';
import { formatResolutionHours } from '../../../shared/utils/durationUtils';

interface MttrSummarySectionProps {
  overallAvgHours?: number;
  categories?: CategoryStatItem[];
}

export const MttrSummarySection: React.FC<MttrSummarySectionProps> = ({
  overallAvgHours,
  categories,
}) => {
  return (
    <div className="space-y-4">
      <div
        data-testid="mttr-overall-banner"
        className="p-3.5 bg-teal-50/70 border border-teal-200 rounded-xl flex items-center justify-between"
      >
        <div className="flex items-center space-x-2.5">
          <div className="p-2 bg-teal-100 text-teal-700 rounded-lg">
            <Timer className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-teal-950">
              전체 평균 해결 시간 (MTTR)
            </div>
            <div className="text-[11px] text-teal-700">
              접수 시각부터 최초 해결 완료까지 소요된 달력 기준 평균 시간 (취소/직권종결 제외)
            </div>
          </div>
        </div>
        <div
          data-testid="mttr-overall-value"
          className="text-lg font-black text-teal-900 shrink-0 ml-3"
        >
          {formatResolutionHours(overallAvgHours)}
        </div>
      </div>

      {Array.isArray(categories) && categories.length > 0 && (
        <div>
          <h4 className="text-xs font-bold text-slate-700 mb-2.5 flex items-center">
            <Layers className="w-4 h-4 mr-1.5 text-indigo-600" /> 카테고리별 티켓 분포 비중 및 평균 해결 시간
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
            {categories.map((cat) => (
              <div
                key={cat.category}
                className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex flex-col justify-between"
              >
                <span className="text-xs text-slate-500 font-medium">{cat.label}</span>
                <div className="flex items-baseline justify-between mt-1.5">
                  <span className="text-base font-bold text-slate-800">{cat.count}건</span>
                  <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">
                    {cat.percentage}%
                  </span>
                </div>
                <div className="mt-1.5 pt-1.5 border-t border-slate-200/70 flex items-center justify-between text-[11px] text-slate-500">
                  <span>평균 해결</span>
                  <span className="font-semibold text-teal-700">
                    {formatResolutionHours(cat.avg_resolution_hours, undefined, '-')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
