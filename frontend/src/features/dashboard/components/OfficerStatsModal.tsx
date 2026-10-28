import React from 'react';
import {
  X,
  BarChart3,
  Users,
  Star,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Loader2,
  Layers,
} from 'lucide-react';
import { useOfficerStats } from '../hooks/useOfficerStats';
import { OfficerStatItem } from '../types/dashboard';

export interface OfficerStatsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const OfficerStatsModal: React.FC<OfficerStatsModalProps> = ({ isOpen, onClose }) => {
  const { data, loading, error } = useOfficerStats(isOpen);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden border border-slate-100">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-indigo-100 text-indigo-700 rounded-xl">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">IT 담당자별 처리 실적 및 카테고리 통계</h3>
              <p className="text-xs text-slate-500">배정 티켓 현황, SLA 준수율, 만족도 평점 현황</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center text-slate-400">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-600 mb-2" />
              <p className="text-sm font-medium">통계 데이터를 산출하는 중입니다...</p>
            </div>
          ) : error ? (
            <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-center text-sm">
              {error}
            </div>
          ) : !data ? null : (
            <>
              {/* Overall KPI Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-indigo-50/60 border border-indigo-100 p-3.5 rounded-xl">
                  <div className="flex items-center text-xs text-indigo-700 font-semibold mb-1">
                    <Users className="w-3.5 h-3.5 mr-1" /> 활성 IT 인력
                  </div>
                  <div className="text-xl font-black text-indigo-950">
                    {data.officers.length}명
                  </div>
                </div>

                <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-xl">
                  <div className="flex items-center text-xs text-slate-600 font-semibold mb-1">
                    <Clock className="w-3.5 h-3.5 mr-1" /> 전체 진행중 티켓
                  </div>
                  <div className="text-xl font-black text-slate-800">
                    {(data as any).total_active_tickets ?? 0}건
                  </div>
                  <div className="text-[11px] text-amber-600 mt-0.5">
                    (미배정: {(data as any).unassigned_count ?? 0}건)
                  </div>
                </div>

                <div className="bg-emerald-50/60 border border-emerald-100 p-3.5 rounded-xl">
                  <div className="flex items-center text-xs text-emerald-700 font-semibold mb-1">
                    <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> 전체 SLA 준수율
                  </div>
                  <div className="text-xl font-black text-emerald-950">
                    {(data as any).overall_sla_rate ?? 0}%
                  </div>
                </div>

                <div className="bg-amber-50/60 border border-amber-100 p-3.5 rounded-xl">
                  <div className="flex items-center text-xs text-amber-700 font-semibold mb-1">
                    <Star className="w-3.5 h-3.5 mr-1" /> 전체 만족도 평점
                  </div>
                  <div className="text-xl font-black text-amber-950">
                    {(data as any).overall_avg_rating > 0 ? `${(data as any).overall_avg_rating}점` : '평가 없음'}
                  </div>
                </div>
              </div>

              {/* Officer Performance Table */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 mb-2.5 flex items-center">
                  <Users className="w-4 h-4 mr-1.5 text-indigo-600" /> 담당자별 세부 실적 지표
                </h4>
                <div className="border border-slate-200 rounded-xl overflow-hidden shadow-xs">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
                        <th className="py-2.5 px-3">담당자</th>
                        <th className="py-2.5 px-3 text-center">배정 총합</th>
                        <th className="py-2.5 px-3 text-center">처리중</th>
                        <th className="py-2.5 px-3 text-center">해결완료</th>
                        <th className="py-2.5 px-3 text-center">기한초과</th>
                        <th className="py-2.5 px-3 text-center">SLA 준수율</th>
                        <th className="py-2.5 px-3 text-center">만족도 평점</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {data.officers.length === 0 ? (
                        <tr>
                          <td colSpan={7} className="py-6 text-center text-slate-400">
                            등록된 IT 담당자가 없습니다.
                          </td>
                        </tr>
                      ) : (
                        data.officers.map((officer: OfficerStatItem) => (
                          <tr key={officer.id || (officer as any).officer_id} className="hover:bg-slate-50/80 transition-colors">
                            <td className="py-2.5 px-3 font-semibold text-slate-900">
                              {officer.name || (officer as any).officer_name}
                              <span className="block text-[10px] text-slate-400 font-normal">
                                {(officer as any).officer_email || ''}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-center font-bold text-indigo-600">
                              {officer.total_assigned}건
                            </td>
                            <td className="py-2.5 px-3 text-center text-blue-600 font-medium">
                              {(officer as any).in_progress_count ?? officer.in_progress}
                            </td>
                            <td className="py-2.5 px-3 text-center text-emerald-600 font-medium">
                              {(officer as any).resolved_count ?? officer.resolved}
                            </td>
                            <td className="py-2.5 px-3 text-center">
                              {((officer as any).overdue_count ?? 0) > 0 ? (
                                <span className="inline-flex items-center text-rose-600 font-bold bg-rose-50 px-1.5 py-0.5 rounded">
                                  <AlertTriangle className="w-3 h-3 mr-0.5" />
                                  {(officer as any).overdue_count}
                                </span>
                              ) : (
                                <span className="text-slate-400">0</span>
                              )}
                            </td>
                            <td className="py-2.5 px-3 text-center font-semibold">
                              <span
                                className={
                                  ((officer as any).sla_compliance_rate ?? 100) >= 90
                                    ? 'text-emerald-700'
                                    : ((officer as any).sla_compliance_rate ?? 100) >= 70
                                    ? 'text-amber-700'
                                    : 'text-rose-700'
                                }
                              >
                                {(officer as any).sla_compliance_rate ?? 100}%
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-center">
                              {((officer as any).rating_count ?? 0) > 0 ? (
                                <span className="inline-flex items-center text-amber-700 font-bold">
                                  <Star className="w-3.5 h-3.5 mr-0.5 fill-amber-400 text-amber-400" />
                                  {(officer as any).avg_rating}
                                  <span className="text-[10px] text-slate-400 ml-1 font-normal">
                                    ({(officer as any).rating_count}건)
                                  </span>
                                </span>
                              ) : (
                                <span className="text-slate-400">-</span>
                              )}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Category Breakdown */}
              {Array.isArray((data as any).category_breakdown) && (
                <div>
                  <h4 className="text-xs font-bold text-slate-700 mb-2.5 flex items-center">
                    <Layers className="w-4 h-4 mr-1.5 text-indigo-600" /> 카테고리별 티켓 분포 비중
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                    {((data as any).category_breakdown as any[]).map((cat: any) => (
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
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-semibold text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
};
