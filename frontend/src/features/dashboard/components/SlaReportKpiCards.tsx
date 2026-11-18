import React from 'react';
import {
  Inbox,
  CheckCircle2,
  ShieldCheck,
  Clock,
  AlertTriangle,
  PauseCircle,
} from 'lucide-react';
import { SlaReportSummary } from '../types/slaReport';
import { formatOnTimeRate, formatReportHours } from '../utils/slaReport';

interface SlaReportKpiCardsProps {
  summary: SlaReportSummary;
}

export const SlaReportKpiCards: React.FC<SlaReportKpiCardsProps> = ({ summary }) => {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
      <div className="bg-slate-50 border border-slate-200 p-3 rounded-xl">
        <div className="flex items-center text-[11px] font-semibold text-slate-600 mb-1">
          <Inbox className="w-3.5 h-3.5 mr-1 text-indigo-600" /> 기간 접수
        </div>
        <div className="text-lg font-black text-slate-900">{summary.created}건</div>
        <div className="text-[11px] text-slate-500 mt-0.5">현재 미완료 {summary.open_now}건</div>
      </div>

      <div className="bg-indigo-50/60 border border-indigo-100 p-3 rounded-xl">
        <div className="flex items-center text-[11px] font-semibold text-indigo-700 mb-1">
          <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> 최초 해결
        </div>
        <div className="text-lg font-black text-indigo-950">{summary.resolved}건</div>
        <div className="text-[11px] text-indigo-700 mt-0.5">
          준수 {summary.on_time} / 지연 {summary.breached}
        </div>
      </div>

      <div className="bg-emerald-50/60 border border-emerald-100 p-3 rounded-xl">
        <div className="flex items-center text-[11px] font-semibold text-emerald-700 mb-1">
          <ShieldCheck className="w-3.5 h-3.5 mr-1" /> SLA 준수율
        </div>
        <div className="text-lg font-black text-emerald-950">
          {formatOnTimeRate(summary.on_time_rate)}
        </div>
        <div className="text-[11px] text-emerald-700 mt-0.5">최초 해결 기준</div>
      </div>

      <div className="bg-teal-50/60 border border-teal-100 p-3 rounded-xl">
        <div className="flex items-center text-[11px] font-semibold text-teal-700 mb-1">
          <Clock className="w-3.5 h-3.5 mr-1" /> 평균 해결시간
        </div>
        <div className="text-lg font-black text-teal-950">
          {formatReportHours(summary.avg_resolution_hours)}
        </div>
        <div className="text-[11px] text-teal-700 mt-0.5">접수~최초해결</div>
      </div>

      <div className="bg-rose-50/60 border border-rose-100 p-3 rounded-xl">
        <div className="flex items-center text-[11px] font-semibold text-rose-700 mb-1">
          <AlertTriangle className="w-3.5 h-3.5 mr-1" /> 현재 기한 초과
        </div>
        <div className="text-lg font-black text-rose-950">{summary.overdue_now}건</div>
        <div className="text-[11px] text-rose-600 mt-0.5">진행 중 기준</div>
      </div>

      <div className="bg-amber-50/60 border border-amber-100 p-3 rounded-xl">
        <div className="flex items-center text-[11px] font-semibold text-amber-700 mb-1">
          <PauseCircle className="w-3.5 h-3.5 mr-1" /> 현재 일시정지
        </div>
        <div className="text-lg font-black text-amber-950">{summary.paused_now}건</div>
        <div className="text-[11px] text-amber-700 mt-0.5">
          평균 정지 {formatReportHours(summary.avg_paused_hours)}
        </div>
      </div>
    </div>
  );
};
