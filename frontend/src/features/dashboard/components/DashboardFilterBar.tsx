import React from 'react';
import { Search, RotateCcw, Clock, AlertTriangle } from 'lucide-react';

interface DashboardFilterBarProps {
  isOfficer: boolean;
  activeTab: 'all' | 'faq';
  onTabChange: (tab: 'all' | 'faq') => void;
  search: string;
  onSearchChange: (val: string) => void;
  isOverdueOnly: boolean;
  onToggleOverdue: () => void;
  statusFilter: string;
  onStatusChange: (val: string) => void;
  categoryFilter: string;
  onCategoryChange: (val: string) => void;
  priorityFilter: string;
  onPriorityChange: (val: string) => void;
  sortBy: string;
  onSortByChange: (val: string) => void;
  hasActiveFilters: boolean;
  onResetFilters: () => void;
}

export const DashboardFilterBar: React.FC<DashboardFilterBarProps> = ({
  isOfficer,
  activeTab,
  onTabChange,
  search,
  onSearchChange,
  isOverdueOnly,
  onToggleOverdue,
  statusFilter,
  onStatusChange,
  categoryFilter,
  onCategoryChange,
  priorityFilter,
  onPriorityChange,
  sortBy,
  onSortByChange,
  hasActiveFilters,
  onResetFilters,
}) => {
  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-4 mb-6 shadow-xs flex flex-col gap-3.5">
      {/* Row 1: Tabs & Search + Overdue Toggle */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl w-fit">
          <button
            type="button"
            onClick={() => onTabChange('all')}
            className={`px-3.5 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer ${
              activeTab === 'all'
                ? 'bg-white text-indigo-700 shadow-2xs'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            {isOfficer ? '전체 문의' : '내 문의 목록'}
          </button>
          <button
            type="button"
            onClick={() => onTabChange('faq')}
            className={`px-3.5 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer ${
              activeTab === 'faq'
                ? 'bg-white text-indigo-700 shadow-2xs'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            사내 FAQ
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Real-time search */}
          <div className="relative flex-1 sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="문의 번호, 제목 검색..."
              className="w-full text-xs pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
            />
          </div>

          {/* Overdue toggle */}
          <button
            type="button"
            onClick={onToggleOverdue}
            className={`flex items-center text-xs px-3 py-2 rounded-xl font-medium border transition-all cursor-pointer shrink-0 ${
              isOverdueOnly
                ? 'bg-rose-50 text-rose-700 border-rose-300 font-bold'
                : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
            }`}
          >
            <Clock className="w-3.5 h-3.5 mr-1.5 text-rose-500" />
            기한 초과만
          </button>
        </div>
      </div>

      {/* Row 2: Status, Category, Priority, Sort Dropdowns & Reset */}
      <div className="border-t border-slate-100 pt-3 flex flex-wrap items-center justify-between gap-2.5">
        <div className="flex flex-wrap items-center gap-2">
          {/* Status Dropdown */}
          <select
            value={statusFilter}
            onChange={(e) => onStatusChange(e.target.value)}
            className="text-xs border border-slate-300 rounded-xl px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
          >
            <option value="">전체 상태</option>
            <option value="submitted">접수대기</option>
            <option value="assigned">배정완료</option>
            <option value="in_progress">처리중</option>
            <option value="pending">답변대기</option>
            <option value="resolved">해결완료</option>
            <option value="closed">종결</option>
            <option value="canceled">취소</option>
          </select>

          {/* Category Dropdown */}
          <select
            value={categoryFilter}
            onChange={(e) => onCategoryChange(e.target.value)}
            className="text-xs border border-slate-300 rounded-xl px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
          >
            <option value="">전체 분류</option>
            <option value="hw">하드웨어</option>
            <option value="sw">소프트웨어</option>
            <option value="network">네트워크</option>
            <option value="account">계정/권한</option>
            <option value="etc">기타</option>
          </select>

          {/* Priority Dropdown */}
          <select
            value={priorityFilter}
            onChange={(e) => onPriorityChange(e.target.value)}
            className="text-xs border border-slate-300 rounded-xl px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
          >
            <option value="">전체 긴급도</option>
            <option value="3">긴급</option>
            <option value="2">높음</option>
            <option value="1">보통</option>
            <option value="0">낮음</option>
          </select>

          {/* Sort Dropdown */}
          <select
            value={sortBy}
            onChange={(e) => onSortByChange(e.target.value)}
            className="text-xs border border-slate-300 rounded-xl px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer font-medium text-slate-700"
          >
            <option value="id desc">최신 등록순</option>
            <option value="id asc">오래된 등록순</option>
            <option value="deadline asc">SLA 마감 임박순</option>
            <option value="priority desc">긴급도 높은순</option>
            <option value="write_date desc">최근 조치/수정순</option>
          </select>
        </div>

        {/* Reset Filters */}
        {hasActiveFilters && (
          <button
            type="button"
            onClick={onResetFilters}
            className="text-xs font-semibold text-slate-500 hover:text-slate-800 flex items-center px-2.5 py-1.5 rounded-lg hover:bg-slate-100 transition-all cursor-pointer shrink-0 ml-auto"
          >
            <RotateCcw className="w-3.5 h-3.5 mr-1" />
            필터 초기화
          </button>
        )}
      </div>
    </div>
  );
};
