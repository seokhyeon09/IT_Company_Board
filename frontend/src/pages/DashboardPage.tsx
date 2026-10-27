import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { apiClient } from '../api/client';
import { TicketCard, Ticket } from '../components/TicketCard';
import { TicketCreateModal } from '../components/TicketCreateModal';
import { TicketDetailModal } from '../components/TicketDetailModal';
import { DashboardStats, TicketStats } from '../components/DashboardStats';
import { FaqAccordion } from '../components/FaqAccordion';
import {
  Plus,
  Search,
  RefreshCw,
  BookOpen,
  Inbox,
  X,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
} from 'lucide-react';

const PAGE_SIZE = 12;

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<TicketStats | null>(null);

  // Modals
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);

  // Filters
  const [activeTab, setActiveTab] = useState<'all' | 'faq'>('all');
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [isOverdueOnly, setIsOverdueOnly] = useState(false);

  // Pagination
  const [page, setPage] = useState(1);

  // Debounce search input (300ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(handler);
  }, [search]);

  // Fetch KPI Stats
  const fetchStats = async () => {
    try {
      const res = await apiClient.get('/tickets/stats');
      setStats(res.data.data);
    } catch (err) {
      console.error('Failed to fetch ticket stats:', err);
    }
  };

  // Fetch Tickets List
  const fetchTickets = async () => {
    setLoading(true);
    try {
      const params: any = {
        offset: (page - 1) * PAGE_SIZE,
        limit: PAGE_SIZE,
      };

      if (debouncedSearch.trim()) params.search = debouncedSearch.trim();
      if (statusFilter) params.status = statusFilter;
      if (categoryFilter) params.category = categoryFilter;
      if (priorityFilter) params.priority = priorityFilter;
      if (isOverdueOnly) params.is_overdue = true;

      if (activeTab === 'faq') {
        params.is_faq = true;
      }

      const res = await apiClient.get('/tickets', { params });
      setTickets(res.data.data || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error('Failed to fetch tickets:', err);
    } finally {
      setLoading(false);
    }
  };

  // Trigger list fetch when filter states change
  useEffect(() => {
    fetchTickets();
  }, [activeTab, debouncedSearch, statusFilter, categoryFilter, priorityFilter, isOverdueOnly, page]);

  // Initial stats fetch
  useEffect(() => {
    fetchStats();
  }, []);

  const refreshAll = () => {
    fetchStats();
    fetchTickets();
  };

  const handleStatsCardClick = (targetStatus: string) => {
    setPage(1);
    if (targetStatus === 'overdue') {
      setIsOverdueOnly((prev) => !prev);
      setStatusFilter('');
    } else {
      setIsOverdueOnly(false);
      setStatusFilter((prev) => (prev === targetStatus ? '' : targetStatus));
    }
  };

  const resetFilters = () => {
    setSearch('');
    setDebouncedSearch('');
    setStatusFilter('');
    setCategoryFilter('');
    setPriorityFilter('');
    setIsOverdueOnly(false);
    setActiveTab('all');
    setPage(1);
  };

  const hasActiveFilters = Boolean(
    search || statusFilter || categoryFilter || priorityFilter || isOverdueOnly || activeTab !== 'all'
  );

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Top Banner & Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">IT 지원 대시보드</h2>
          <p className="text-sm text-slate-500 mt-1">
            {user?.is_officer
              ? 'IT 담당자 전용: 전체 티켓 현황, SLA 모니터링 및 조치 관리를 수행합니다.'
              : '사원 전용: 내 문의 내역 및 사내 FAQ 지식창고를 확인합니다.'}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={refreshAll}
            className="p-2.5 text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl transition-all shadow-xs"
            title="새로고침"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm rounded-xl shadow-md shadow-indigo-500/20 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            새 문의 접수
          </button>
        </div>
      </div>

      {/* KPI Stats Widgets */}
      <DashboardStats
        stats={stats}
        selectedStatus={isOverdueOnly ? 'overdue' : statusFilter}
        onSelectStatus={handleStatsCardClick}
      />

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 mb-6 shadow-xs flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left: View Tabs */}
        <div className="flex space-x-2">
          <button
            onClick={() => {
              setActiveTab('all');
              setPage(1);
            }}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'all'
                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-xs'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            {user?.is_officer ? '전체 문의 목록' : '내 문의 내역'}
          </button>
          <button
            onClick={() => {
              setActiveTab('faq');
              setPage(1);
            }}
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

        {/* Right: Multi Filters */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Debounced Search Input */}
          <div className="relative">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="접수번호, 제목 실시간 검색..."
              className="pl-8 pr-7 py-2 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 w-44 sm:w-56 transition-all"
            />
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-3" />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-2 top-2.5 text-slate-400 hover:text-slate-600 p-0.5"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Status Dropdown */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setIsOverdueOnly(false);
              setPage(1);
            }}
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
            onChange={(e) => {
              setCategoryFilter(e.target.value);
              setPage(1);
            }}
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
            onChange={(e) => {
              setPriorityFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs border border-slate-300 rounded-xl px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
          >
            <option value="">전체 우선순위</option>
            <option value="3">긴급</option>
            <option value="2">높음</option>
            <option value="1">보통</option>
            <option value="0">낮음</option>
          </select>

          {/* Overdue Quick Filter Toggle */}
          <button
            onClick={() => {
              setIsOverdueOnly((prev) => !prev);
              setPage(1);
            }}
            className={`flex items-center px-3 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
              isOverdueOnly
                ? 'bg-rose-50 border-rose-300 text-rose-700 shadow-xs'
                : 'bg-white border-slate-300 text-slate-600 hover:bg-slate-50'
            }`}
          >
            <AlertTriangle className={`w-3.5 h-3.5 mr-1.5 ${isOverdueOnly ? 'text-rose-600' : 'text-slate-400'}`} />
            기한 초과만
          </button>

          {/* Reset Filters Button */}
          {hasActiveFilters && (
            <button
              onClick={resetFilters}
              className="flex items-center px-3 py-2 text-xs text-slate-500 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all cursor-pointer"
              title="필터 초기화"
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1" />
              초기화
            </button>
          )}
        </div>
      </div>

      {/* Ticket Grid List */}
      {loading ? (
        <div className="py-20 text-center text-slate-400 text-sm flex flex-col items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-indigo-500 mb-3" />
          티켓 목록을 불러오는 중입니다...
        </div>
      ) : tickets.length === 0 ? (
        <div className="py-24 text-center bg-white rounded-3xl border border-slate-200 shadow-xs flex flex-col items-center justify-center">
          <Inbox className="w-12 h-12 text-slate-300 mb-3" />
          <h3 className="font-bold text-slate-700 text-base">조회된 문의 내역이 없습니다</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm">
            {hasActiveFilters
              ? '지정한 검색어나 필터 조건에 일치하는 항목이 없습니다.'
              : '등록된 티켓이 없습니다. 상단의 "새 문의 접수" 버튼을 눌러 티켓을 등록해보세요.'}
          </p>
          {hasActiveFilters && (
            <button
              onClick={resetFilters}
              className="mt-4 px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold rounded-xl transition-all cursor-pointer"
            >
              모든 필터 초기화
            </button>
          )}
        </div>
      ) : (
        <>
          {activeTab === 'faq' ? (
            <FaqAccordion
              tickets={tickets}
              onSelectTicket={(id) => setSelectedTicketId(id)}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {tickets.map((ticket) => (
                <TicketCard
                  key={ticket.id}
                  ticket={ticket}
                  onClick={(t) => setSelectedTicketId(t.id)}
                />
              ))}
            </div>
          )}

          {/* Pagination Controls */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-200 pt-6">
            <div className="text-xs text-slate-500 font-medium">
              전체 <span className="font-bold text-slate-900">{total}</span>개 중{' '}
              <span className="font-bold text-slate-900">{(page - 1) * PAGE_SIZE + 1}</span>-
              <span className="font-bold text-slate-900">{Math.min(page * PAGE_SIZE, total)}</span>개 표시
            </div>

            <div className="flex items-center space-x-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="flex items-center px-3 py-1.5 text-xs font-semibold rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                <ChevronLeft className="w-3.5 h-3.5 mr-1" />
                이전
              </button>

              <div className="flex items-center space-x-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => {
                  // Display page numbers near current page
                  if (
                    pageNum === 1 ||
                    pageNum === totalPages ||
                    (pageNum >= page - 1 && pageNum <= page + 1)
                  ) {
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`w-8 h-8 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                          page === pageNum
                            ? 'bg-indigo-600 text-white shadow-xs'
                            : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  }
                  if (pageNum === page - 2 || pageNum === page + 2) {
                    return (
                      <span key={pageNum} className="text-slate-400 px-1 text-xs">
                        ...
                      </span>
                    );
                  }
                  return null;
                })}
              </div>

              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="flex items-center px-3 py-1.5 text-xs font-semibold rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                다음
                <ChevronRight className="w-3.5 h-3.5 ml-1" />
              </button>
            </div>
          </div>
        </>
      )}

      {/* Ticket Create Modal */}
      <TicketCreateModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={refreshAll}
      />

      {/* Ticket Detail Modal */}
      <TicketDetailModal
        isOpen={selectedTicketId !== null}
        ticketId={selectedTicketId}
        onClose={() => setSelectedTicketId(null)}
        onSuccess={refreshAll}
      />
    </div>
  );
};
