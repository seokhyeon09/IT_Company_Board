import React from 'react';
import { Layers, Flag } from 'lucide-react';
import { SlaReportCategoryItem, SlaReportPriorityItem } from '../types/slaReport';
import { formatOnTimeRate, formatReportHours } from '../utils/slaReport';

interface SlaReportBreakdownTablesProps {
  categories: SlaReportCategoryItem[];
  priorities: SlaReportPriorityItem[];
}

function renderRateText(rate: number | null) {
  if (rate === null) {
    return <span className="text-slate-400">-</span>;
  }
  const color =
    rate >= 90 ? 'text-emerald-700' : rate >= 70 ? 'text-amber-700' : 'text-rose-700';
  return <span className={`font-semibold ${color}`}>{formatOnTimeRate(rate)}</span>;
}

export const SlaReportBreakdownTables: React.FC<SlaReportBreakdownTablesProps> = ({
  categories,
  priorities,
}) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div>
        <h4 className="text-xs font-bold text-slate-700 mb-2 flex items-center">
          <Layers className="w-4 h-4 mr-1.5 text-indigo-600" /> 분야별 현황
        </h4>
        <div className="border border-slate-200 rounded-xl overflow-hidden bg-white">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                <th className="py-2 px-3">분야</th>
                <th className="py-2 px-3 text-center">접수</th>
                <th className="py-2 px-3 text-center">해결</th>
                <th className="py-2 px-3 text-center">SLA 준수율</th>
                <th className="py-2 px-3 text-center">평균 해결시간</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {categories.map((row) => (
                <tr key={row.category} className="hover:bg-slate-50/70">
                  <td className="py-2 px-3 font-semibold text-slate-900">{row.label}</td>
                  <td className="py-2 px-3 text-center">{row.created}건</td>
                  <td className="py-2 px-3 text-center">{row.resolved}건</td>
                  <td className="py-2 px-3 text-center">{renderRateText(row.on_time_rate)}</td>
                  <td className="py-2 px-3 text-center text-teal-700 font-medium">
                    {formatReportHours(row.avg_resolution_hours)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div>
        <h4 className="text-xs font-bold text-slate-700 mb-2 flex items-center">
          <Flag className="w-4 h-4 mr-1.5 text-indigo-600" /> 긴급도별 현황
        </h4>
        <div className="border border-slate-200 rounded-xl overflow-hidden bg-white">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                <th className="py-2 px-3">긴급도</th>
                <th className="py-2 px-3 text-center">접수</th>
                <th className="py-2 px-3 text-center">해결</th>
                <th className="py-2 px-3 text-center">SLA 준수율</th>
                <th className="py-2 px-3 text-center">평균 해결시간</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {priorities.map((row) => (
                <tr key={row.priority} className="hover:bg-slate-50/70">
                  <td className="py-2 px-3 font-semibold text-slate-900">{row.label}</td>
                  <td className="py-2 px-3 text-center">{row.created}건</td>
                  <td className="py-2 px-3 text-center">{row.resolved}건</td>
                  <td className="py-2 px-3 text-center">{renderRateText(row.on_time_rate)}</td>
                  <td className="py-2 px-3 text-center text-teal-700 font-medium">
                    {formatReportHours(row.avg_resolution_hours)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
