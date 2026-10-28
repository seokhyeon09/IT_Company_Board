import React from 'react';
import {
  Search,
  BookOpen,
  X,
  RotateCcw,
  AlertTriangle,
} from 'lucide-react';

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
    <div className="bg-white rounded-2xl border border-slate-200 p-4 mb-6 shadow-xs space-y-3.5">
      {/* Row 1: Left Tabs & Right Search/Overdue */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Left: View Tabs */}
        <div className="flex space-x-2">
          <button
            type="button"
            onClick={() => onTabChange('all')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'all'
                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            {isOfficer ? '전체 문의 목록' : '내 문의 내역'}
          </button>
          <button
            type="button"
            onClick={() => onTabChange('faq')}
            className={`flex items-center px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'faq'
                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 mr-1.5" />
            FAQ 지식창고
          </button>
        </div>

        {/* Right: Search & Overdue Toggle Switch */}
        <div className="flex items-center gap-2.5">
          {/* Debounced Search Input */}
          <div className="relative">
            <input
              type="text"
              value={search}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="접수번호, 제목 실시간 검색..."
              className="pl-8 pr-7 py-2 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 w-44 sm:w-56 transition-all bg-white"
            />
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-3" />
            {search && (
              <button
                type="button"
                onClick={() => onSearchChange('')}
                className="absolute right-2 top-2.5 text-slate-400 hover:text-slate-600 p-0.5 cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Overdue Toggle Switch */}
          <button
            type="button"
            role="switch"
            aria-checked={isOverdueOnly}
            onClick={onToggleOverdue}
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              isOverdueOnly
                ? 'bg-rose-50 border-rose-300 text-rose-700 shadow-xs'
                : 'bg-white border-slate-300 text-slate-600 hover:bg-slate-50'
            }`}
          >
            <div
              className={`w-7 h-4 flex items-center rounded-full p-0.5 transition-colors ${
                isOverdueOnly ? 'bg-rose-600' : 'bg-slate-300'
              }`}
            >
              <div
                className={`bg-white w-3 h-3 rounded-full shadow-xs transform transition-transform ${
                  isOverdueOnly ? 'translate-x-3' : 'translate-x-0'
                }`}
              />
            </div>
            <AlertTriangle
              className={`w-3.5 h-3.5 ${
                isOverdueOnly ? 'text-rose-600' : 'text-slate-400'
              }`}
            />
            <span>기한 초과만</span>
          </button>
        </div>
      </div>

      {/* Row 2: Multi Filter Selects & Sort */}
      <div className="border-t border-slate-100 pt-3 flex flex-wrap items-center justify-between gap-2.5">
        <div className="flex flex-wrap items-center gap-2">
          {/* Status Dropdown */}
          <select
            value={statusFilter === 'overdue' ? '' : statusFilter}
            onChange={(e) => onStatusChange(e.target.value)}
            className="text-xs border border-slate-300 rounded-xl px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
          >
            <option value="">전체 상태</option>
            <option value="waiting">접수/배정 (전체)</option>
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
            <option value="">전체 카테고리</option>
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
            <option value="">전체 우선순위</option>
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
            <option value="write_date desc">최근 업데이트순</option>
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
