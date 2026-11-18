import React from 'react';
import { Plus, RefreshCw, BarChart3, Mail } from 'lucide-react';
import { UserProfile } from '../../../stores/authStore';

interface DashboardHeaderProps {
  user: UserProfile | null;
  unreadCount: number;
  onRefresh: () => void;
  onOpenEmailModal: () => void;
  onOpenOfficerStats: () => void;
  onOpenCreateModal: () => void;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  user,
  unreadCount,
  onRefresh,
  onOpenEmailModal,
  onOpenOfficerStats,
  onOpenCreateModal,
}) => {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
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
  );
};
