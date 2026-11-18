import React from 'react';
import { Plus, RefreshCw, BarChart3, Mail, Download, Loader2, FileBarChart2 } from 'lucide-react';
import { UserProfile } from '../../../stores/authStore';
import { TicketExportState } from '../types/dashboard';
import { OfficerAbsenceControl } from './OfficerAbsenceControl';

interface DashboardHeaderProps {
  user: UserProfile | null;
  unreadCount: number;
  exportState?: TicketExportState;
  onRefresh: () => void;
  onOpenEmailModal: () => void;
  onOpenOfficerStats: () => void;
  onOpenSlaReport?: () => void;
  onOpenCreateModal: () => void;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  user,
  unreadCount,
  exportState,
  onRefresh,
  onOpenEmailModal,
  onOpenOfficerStats,
  onOpenSlaReport,
  onOpenCreateModal,
}) => {
  return (
    <div className="mb-8 space-y-2">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">IT 지원 대시보드</h2>
          <p className="text-sm text-slate-500 mt-1">
            {user?.is_admin || user?.is_manager
              ? 'IT 관리자 전용: 전사 티켓 통합 제어, 직권 조치 및 SLA 성과 통계를 관리합니다.'
              : user?.is_officer
              ? 'IT 담당자 전용: 전체 티켓 현황, SLA 모니터링 및 조치 관리를 수행합니다.'
              : '사원 전용: 내 문의 내역 및 사내 FAQ 지식창고를 확인합니다.'}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 md:shrink-0">
          <button
            type="button"
            onClick={onRefresh}
            className="flex items-center whitespace-nowrap text-xs font-semibold text-slate-600 bg-white hover:bg-slate-50 border border-slate-200 px-3 py-2 rounded-xl transition-all shadow-xs cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
            새로고침
          </button>

          {user?.is_officer && <OfficerAbsenceControl />}

          {user?.is_officer && exportState && (
            <button
              type="button"
              disabled={exportState.exporting}
              onClick={exportState.onExport}
              className="flex items-center whitespace-nowrap text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 px-3 py-2 rounded-xl transition-all shadow-xs cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {exportState.exporting ? (
                <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin text-slate-500" />
              ) : (
                <Download className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
              )}
              {exportState.exporting ? '내보내는 중...' : 'CSV 내보내기'}
            </button>
          )}

          <button
            type="button"
            onClick={onOpenEmailModal}
            className="relative flex items-center whitespace-nowrap text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 px-3 py-2 rounded-xl transition-all shadow-xs cursor-pointer"
          >
            <Mail className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
            이메일 알림함
            {unreadCount > 0 && (
              <span className="ml-1.5 bg-rose-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center">
                {unreadCount}
              </span>
            )}
          </button>

          {user?.is_officer && (
            <button
              type="button"
              onClick={onOpenOfficerStats}
              className="flex items-center whitespace-nowrap text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 px-3 py-2 rounded-xl transition-all shadow-xs cursor-pointer"
            >
              <BarChart3 className="w-3.5 h-3.5 mr-1.5" />
              담당자별 실적 통계
            </button>
          )}

          {user?.is_officer && onOpenSlaReport && (
            <button
              type="button"
              onClick={onOpenSlaReport}
              className="flex items-center whitespace-nowrap text-xs font-semibold text-teal-700 bg-teal-50 hover:bg-teal-100 border border-teal-200 px-3 py-2 rounded-xl transition-all shadow-xs cursor-pointer"
            >
              <FileBarChart2 className="w-3.5 h-3.5 mr-1.5" />
              SLA 리포트
            </button>
          )}

          <button
            type="button"
            onClick={onOpenCreateModal}
            className="flex items-center whitespace-nowrap text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-xl transition-all shadow-xs cursor-pointer"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            문의 등록
          </button>
        </div>
      </div>

      {exportState?.error && (
        <p className="text-xs text-rose-600 font-medium text-right">{exportState.error}</p>
      )}
      {exportState?.message && !exportState.error && (
        <p className="text-xs text-emerald-700 font-medium text-right">{exportState.message}</p>
      )}
    </div>
  );
};
