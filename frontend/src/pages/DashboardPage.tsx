import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { apiClient, getErrorMessage } from '../api/client';
import { DashboardStats, StatsData } from '../components/DashboardStats';
import { TicketCard, Ticket } from '../features/ticket/components/TicketCard';
import { FaqAccordion, FaqItem } from '../components/FaqAccordion';
import { TicketDetailModal } from '../features/ticket/components/TicketDetailModal';
import { TicketCreateModal } from '../features/ticket/components/TicketCreateModal';
import { DashboardFilterBar } from '../features/dashboard/components/DashboardFilterBar';
import { DashboardPagination } from '../features/dashboard/components/DashboardPagination';
import { Plus, Loader2, Inbox } from 'lucide-react';

const PAGE_SIZE = 12;

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<StatsData>({
    total: 0,
    waiting: 0,
    in_progress: 0,
    resolved: 0,
    overdue: 0,
  });
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [faqs, setFaqs] = useState<FaqItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [activeTab, setActiveTab] = useState<'all' | 'faq'>('all');
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [sortBy, setSortBy] = useState('id desc');
  const [isOverdueOnly, setIsOverdueOnly] = useState(false);

  // Pagination
  const [page, setPage] = useState(1);

  // Modals
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);

  // Search debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  // Fetch Tickets
  const fetchTickets = async () => {
    setLoading(true);
    setError(null);
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
      if (sortBy) params.sort_by = sortBy;

      if (activeTab === 'faq') {
        params.is_faq = true;
        const res = await apiClient.get('/tickets', { params });
        setFaqs(res.data.data || []);
        setTotal(res.data.total || 0);
      } else {
        const res = await apiClient.get('/tickets', { params });
        setTickets(res.data.data || []);
        setTotal(res.data.total || 0);
      }
    } catch (err: any) {
      setError(getErrorMessage(err, '티켓 목록을 불러오지 못했습니다.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [activeTab, debouncedSearch, statusFilter, categoryFilter, priorityFilter, isOverdueOnly, sortBy, page]);

  // Fetch Stats
  const fetchStats = async () => {
    try {
      const res = await apiClient.get('/tickets/stats');
      setStats(res.data.data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

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
    setSortBy('id desc');
    setActiveTab('all');
    setPage(1);
  };

  const hasActiveFilters = Boolean(
    search || statusFilter || categoryFilter || priorityFilter || isOverdueOnly || activeTab !== 'all'
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Banner & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            {user?.is_officer ? 'IT 헬프데스크 관리 센터' : '사내 IT 지원 센터'}
          </h1>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            {user?.name}님 환영합니다. 전산/계정/하드웨어 요청을 신속히 지원합니다.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setIsCreateOpen(true)}
          className="flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2.5 rounded-xl font-bold text-xs shadow-md shadow-indigo-100 hover:shadow-indigo-200 transition-all cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>새 문의 접수</span>
        </button>
      </div>

      {/* KPI Stats Widget */}
      <DashboardStats
        stats={stats}
        selectedStatus={isOverdueOnly ? 'overdue' : statusFilter}
        onSelectStatus={handleStatsCardClick}
      />

      {/* 2-Row Filter Bar */}
      <DashboardFilterBar
        isOfficer={Boolean(user?.is_officer)}
        activeTab={activeTab}
        onTabChange={(tab) => {
          setActiveTab(tab);
          setPage(1);
        }}
        search={search}
        onSearchChange={setSearch}
        isOverdueOnly={isOverdueOnly}
        onToggleOverdue={() => {
          setIsOverdueOnly((prev) => !prev);
          setStatusFilter('');
          setPage(1);
        }}
        statusFilter={statusFilter}
        onStatusChange={(val) => {
          setStatusFilter(val);
          setIsOverdueOnly(false);
          setPage(1);
        }}
        categoryFilter={categoryFilter}
        onCategoryChange={(val) => {
          setCategoryFilter(val);
          setPage(1);
        }}
        priorityFilter={priorityFilter}
        onPriorityChange={(val) => {
          setPriorityFilter(val);
          setPage(1);
        }}
        sortBy={sortBy}
        onSortByChange={(val) => {
          setSortBy(val);
          setPage(1);
        }}
        hasActiveFilters={hasActiveFilters}
        onResetFilters={resetFilters}
      />

      {/* Content Area */}
      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
          <p className="text-xs text-slate-500 font-medium">티켓 목록을 불러오는 중입니다...</p>
        </div>
      ) : error ? (
        <div className="p-8 text-center bg-rose-50 border border-rose-200 rounded-2xl">
          <p className="text-xs text-rose-700 font-semibold">{error}</p>
        </div>
      ) : activeTab === 'faq' ? (
        <FaqAccordion items={faqs} onSelectTicket={(id) => setSelectedTicketId(id)} />
      ) : tickets.length === 0 ? (
        <div className="py-20 flex flex-col items-center justify-center text-center bg-white rounded-2xl border border-slate-200/80 p-6">
          <div className="w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center text-slate-400 mb-3">
            <Inbox className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-slate-700">조회된 티켓이 없습니다</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm">
            {hasActiveFilters
              ? '지정한 검색어나 필터 조건에 일치하는 티켓이 없습니다.'
              : '등록된 티켓이 없습니다. 상단 "새 문의 접수" 버튼을 눌러 티켓을 등록해보세요.'}
          </p>
          {hasActiveFilters && (
            <button
              type="button"
              onClick={resetFilters}
              className="mt-4 px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold rounded-xl transition-all cursor-pointer"
            >
              모든 필터 초기화
            </button>
          )}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tickets.map((ticket) => (
              <TicketCard
                key={ticket.id}
                ticket={ticket}
                onClick={(t) => setSelectedTicketId(t.id)}
              />
            ))}
          </div>

          <DashboardPagination
            page={page}
            total={total}
            pageSize={PAGE_SIZE}
            onPageChange={(newPage) => setPage(newPage)}
          />
        </>
      )}

      {/* Modals */}
      <TicketCreateModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSuccess={() => {
          fetchTickets();
          fetchStats();
        }}
      />

      <TicketDetailModal
        isOpen={selectedTicketId !== null}
        ticketId={selectedTicketId}
        onClose={() => setSelectedTicketId(null)}
        onSuccess={() => {
          fetchTickets();
          fetchStats();
        }}
      />
    </div>
  );
};
