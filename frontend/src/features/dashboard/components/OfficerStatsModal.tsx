import React, { useEffect, useState } from 'react';
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
import { apiClient, getErrorMessage } from '../../../api/client';
import { OfficerStatsData } from '../../ticket/types/ticket';

export interface OfficerStatsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const OfficerStatsModal: React.FC<OfficerStatsModalProps> = ({ isOpen, onClose }) => {
  const [data, setData] = useState<OfficerStatsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    const fetchOfficerStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.get('/tickets/officer-stats');
        setData(res.data.data);
      } catch (err: any) {
        setError(getErrorMessage(err, '담당자별 통계 정보를 불러오지 못했습니다.'));
      } finally {
        setLoading(false);
      }
    };
    fetchOfficerStats();
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden border border-slate-100">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-indigo-600 text-white rounded-xl shadow-xs">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">담당자별 처리 실적 및 카테고리 통계</h2>
              <p className="text-xs text-slate-500">
                IT 담당자별 배정·해결 현황, SLA 기한 준수율 및 만족도 평점을 실시간 집계합니다.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/60 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {loading ? (
            <div className="py-20 text-center text-slate-400 flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mb-3" />
              통계 데이터를 집계하는 중입니다...
            </div>
          ) : error ? (
            <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-center text-xs font-semibold">
              {error}
            </div>
          ) : data ? (
            <>
              {/* Top Overview KPI Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="flex items-center justify-between text-xs text-slate-500 font-semibold mb-1">
                    <span>전체 유효 문의</span>
                    <Layers className="w-4 h-4 text-indigo-500" />
                  </div>
                  <p className="text-2xl font-black text-slate-900">{data.total_active_tickets}건</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">취소 제외 전체 누적</p>
                </div>

                <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200">
                  <div className="flex items-center justify-between text-xs text-amber-800 font-semibold mb-1">
                    <span>미배정 접수대기</span>
                    <Clock className="w-4 h-4 text-amber-600" />
                  </div>
                  <p className="text-2xl font-black text-amber-900">{data.unassigned_count}건</p>
                  <p className="text-[11px] text-amber-700 mt-0.5">담당자 배정 필요</p>
                </div>

                <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-200">
                  <div className="flex items-center justify-between text-xs text-emerald-800 font-semibold mb-1">
                    <span>전체 SLA 준수율</span>
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  </div>
                  <p className="text-2xl font-black text-emerald-900">{data.overall_sla_rate}%</p>
                  <p className="text-[11px] text-emerald-700 mt-0.5">배정 티켓 기한 내 처리율</p>
                </div>

                <div className="p-4 rounded-xl bg-indigo-50/70 border border-indigo-200">
                  <div className="flex items-center justify-between text-xs text-indigo-800 font-semibold mb-1">
                    <span>평균 만족도 평점</span>
                    <Star className="w-4 h-4 text-amber-500 fill-amber-400" />
                  </div>
                  <p className="text-2xl font-black text-indigo-900">
                    {data.overall_avg_rating > 0 ? `${data.overall_avg_rating} / 5.0` : '미집계'}
                  </p>
                  <p className="text-[11px] text-indigo-700 mt-0.5">해결 완료 후 직원 평가 기준</p>
                </div>
              </div>

              {/* Officer Performance Table */}
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <Users className="w-4 h-4 text-indigo-600" />
                  <h3 className="text-sm font-bold text-slate-800">IT 담당자별 업무 처리 현황</h3>
                </div>
                <div className="overflow-x-auto border border-slate-200 rounded-xl">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold text-slate-600 uppercase">
                        <th className="py-3 px-4">담당자</th>
                        <th className="py-3 px-3 text-center">총 배정</th>
                        <th className="py-3 px-3 text-center">진행/대기</th>
                        <th className="py-3 px-3 text-center">해결/종결</th>
                        <th className="py-3 px-3 text-center">기한초과</th>
                        <th className="py-3 px-4">SLA 준수율</th>
                        <th className="py-3 px-4 text-right">평균 만족도</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-xs">
                      {data.officers.map((off) => (
                        <tr key={off.officer_id} className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-3 px-4">
                            <div className="font-bold text-slate-800">{off.officer_name}</div>
                            <div className="text-[11px] text-slate-400">{off.officer_email}</div>
                          </td>
                          <td className="py-3 px-3 text-center font-bold text-slate-700">
                            {off.total_assigned}건
                          </td>
                          <td className="py-3 px-3 text-center">
                            <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-semibold">
                              {off.in_progress_count}건
                            </span>
                          </td>
                          <td className="py-3 px-3 text-center">
                            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-semibold">
                              {off.resolved_count}건
                            </span>
                          </td>
                          <td className="py-3 px-3 text-center">
                            {off.overdue_count > 0 ? (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 font-bold">
                                <AlertTriangle className="w-3 h-3 mr-1" />
                                {off.overdue_count}건
                              </span>
                            ) : (
                              <span className="text-slate-400">0건</span>
                            )}
                          </td>
                          <td className="py-3 px-4 w-44">
                            <div className="flex items-center space-x-2">
                              <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                  className={`h-full rounded-full ${
                                    off.sla_compliance_rate >= 90
                                      ? 'bg-emerald-500'
                                      : off.sla_compliance_rate >= 70
                                      ? 'bg-amber-500'
                                      : 'bg-rose-500'
                                  }`}
                                  style={{ width: `${Math.min(100, Math.max(0, off.sla_compliance_rate))}%` }}
                                />
                              </div>
                              <span className="font-bold text-slate-700 w-12 text-right">
                                {off.sla_compliance_rate}%
                              </span>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-right">
                            {off.rating_count > 0 ? (
                              <div className="inline-flex items-center space-x-1 font-bold text-amber-600">
                                <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-500" />
                                <span>{off.avg_rating.toFixed(1)}</span>
                                <span className="text-[11px] text-slate-400 font-normal">
                                  ({off.rating_count}건)
                                </span>
                              </div>
                            ) : (
                              <span className="text-slate-400 text-[11px]">평가 없음</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Category Breakdown */}
              <div>
                <h3 className="text-sm font-bold text-slate-800 mb-3">카테고리별 문의 분포</h3>
                <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
                  {data.category_breakdown.map((cat) => (
                    <div
                      key={cat.category}
                      className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between"
                    >
                      <div className="flex items-center justify-between text-xs font-bold text-slate-700 mb-2">
                        <span>{cat.label}</span>
                        <span className="text-indigo-600">{cat.percentage}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden mb-2">
                        <div
                          className="h-full bg-indigo-500 rounded-full"
                          style={{ width: `${Math.min(100, Math.max(0, cat.percentage))}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-500 font-semibold">{cat.count}건 접수</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 transition-all cursor-pointer"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
};
