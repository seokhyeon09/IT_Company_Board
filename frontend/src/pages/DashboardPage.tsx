import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { apiClient, getErrorMessage } from '../api/client';
import { DashboardStats, TicketStats } from '../components/DashboardStats';
import { TicketCard, Ticket } from '../features/ticket/components/TicketCard';
import { FaqAccordion } from '../components/FaqAccordion';
import { TicketDetailModal } from '../features/ticket/components/TicketDetailModal';
import { TicketCreateModal } from '../features/ticket/components/TicketCreateModal';
import { DashboardFilterBar } from '../features/dashboard/components/DashboardFilterBar';
import { DashboardPagination } from '../features/dashboard/components/DashboardPagination';
import { OfficerStatsModal } from '../features/dashboard/components/OfficerStatsModal';
import { EmailNotificationModal } from '../features/notification/components/EmailNotificationModal';
import { useEmailNotifications } from '../features/notification/hooks/useEmailNotifications';
import { Plus, RefreshCw, Inbox, BarChart3, Mail } from 'lucide-react';

const PAGE_SIZE = 12;

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const mail = useEmailNotifications(user?.uid);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<TicketStats | null>(null);

  // Modals
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);
  const [isOfficerStatsOpen, setIsOfficerStatsOpen] = useState(false);
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);

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
      }

      const res = await apiClient.get('/tickets', { params });
      setTickets(res.data.data || []);
      setTotal(res.data.total || 0);
    } catch (err: any) {
      console.error('Failed to fetch tickets:', err);
      setError(getErrorMessage(err, '티켓 목록을 불러오지 못했습니다.'));
    } finally {
      setLoading(false);
    }
  };

  // Trigger list fetch when filter states change
  useEffect(() => {
    fetchTickets();
  }, [activeTab, debouncedSearch, statusFilter, categoryFilter, priorityFilter, isOverdueOnly, sortBy, page]);

  // Initial stats fetch
  useEffect(() => {
    fetchStats();
  }, []);

  const refreshAll = () => {
    fetchStats();
    fetchTickets();
    mail.refresh();
  };

  const handleStatsCardClick = (targetStatus: string) => {
    setActiveTab('all');
    setPage(1);
    setSortBy('id desc');
    if (targetStatus === '') {
      setStatusFilter('');
    } else {
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

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            type="button"
            onClick={refreshAll}
            className="p-2.5 text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl transition-all shadow-xs cursor-pointer"
            title="새로고침"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            type="button"
            onClick={() => setIsEmailModalOpen(true)}
            className="relative flex items-center px-3.5 py-2.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 font-semibold text-xs rounded-xl shadow-xs transition-all cursor-pointer"
          >
            <Mail className="w-4 h-4 mr-1.5 text-indigo-600" />
            이메일 알림 내역
            {mail.unreadCount > 0 && (
              <span
                className="absolute -top-1.5 -right-1.5 min-w-[18px] h-[18px] px-1 flex items-center justify-center bg-rose-500 text-white text-[10px] font-bold rounded-full ring-2 ring-white"
                title={`미확인 메일 ${mail.unreadCount}건`}
              >
                {mail.unreadCount > 99 ? '99+' : mail.unreadCount}
              </span>
            )}
          </button>
          {user?.is_officer && (
            <button
              type="button"
              onClick={() => setIsOfficerStatsOpen(true)}
              className="flex items-center px-3.5 py-2.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 font-semibold text-xs rounded-xl shadow-xs transition-all cursor-pointer"
            >
              <BarChart3 className="w-4 h-4 mr-1.5 text-indigo-600" />
              담당자별 통계
            </button>
          )}
          <button
            type="button"
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
        selectedStatus={statusFilter}
        onSelectStatus={handleStatsCardClick}
      />

      {/* Filter and Search Bar */}
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
          setPage(1);
        }}
        statusFilter={statusFilter}
        onStatusChange={(val) => {
          setStatusFilter(val);
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

      {/* Ticket Grid List */}
      {loading ? (
        <div className="py-20 text-center text-slate-400 text-sm flex flex-col items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-indigo-500 mb-3" />
          티켓 목록을 불러오는 중입니다...
        </div>
      ) : error ? (
        <div className="p-8 text-center bg-rose-50 border border-rose-200 rounded-2xl">
          <p className="text-xs text-rose-700 font-semibold">{error}</p>
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
          <DashboardPagination
            page={page}
            total={total}
            pageSize={PAGE_SIZE}
            onPageChange={(newPage) => setPage(newPage)}
          />
        </>
      )}

      {/* Ticket Create Modal */}
      <TicketCreateModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={refreshAll}
        onSelectTicket={(id) => setSelectedTicketId(id)}
      />

      {/* Ticket Detail Modal */}
      <TicketDetailModal
        isOpen={selectedTicketId !== null}
        ticketId={selectedTicketId}
        onClose={() => setSelectedTicketId(null)}
        onSuccess={refreshAll}
        onSelectTicket={(id) => setSelectedTicketId(id)}
      />

      {/* Officer Performance & Category Statistics Modal */}
      <OfficerStatsModal
        isOpen={isOfficerStatsOpen}
        onClose={() => setIsOfficerStatsOpen(false)}
      />

      {/* Mock Email Notification Center Modal */}
      <EmailNotificationModal
        isOpen={isEmailModalOpen}
        isOfficer={Boolean(user?.is_officer)}
        items={mail.items}
        loading={mail.loading}
        error={mail.error}
        isRead={mail.isRead}
        onMarkRead={mail.markRead}
        onMarkAllRead={mail.markAllRead}
        onRefresh={mail.refresh}
        onClose={() => setIsEmailModalOpen(false)}
        onSelectTicket={(id) => setSelectedTicketId(id)}
      />
    </div>
  );
};
