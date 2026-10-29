import React, { useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { DashboardStats } from '../components/DashboardStats';
import { TicketCard, Ticket } from '../features/ticket/components/TicketCard';
import { FaqAccordion } from '../components/FaqAccordion';
import { TicketDetailModal } from '../features/ticket/components/TicketDetailModal';
import { TicketCreateModal } from '../features/ticket/components/TicketCreateModal';
import { DashboardFilterBar } from '../features/dashboard/components/DashboardFilterBar';
import { DashboardPagination } from '../features/dashboard/components/DashboardPagination';
import { OfficerStatsModal } from '../features/dashboard/components/OfficerStatsModal';
import { EmailNotificationModal } from '../features/notification/components/EmailNotificationModal';
import { useEmailNotifications } from '../features/notification/hooks/useEmailNotifications';
import { useDashboardTickets } from '../features/dashboard/hooks/useDashboardTickets';
import { Plus, RefreshCw, Inbox, BarChart3, Mail } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const mail = useEmailNotifications(user?.uid);

  const dash = useDashboardTickets();

  // Modals
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);
  const [isOfficerStatsOpen, setIsOfficerStatsOpen] = useState(false);
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);

  const handleRefresh = () => {
    dash.refreshAll();
    mail.refresh();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Top Banner & Action */}
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
        <div className="flex items-center space-x-2 shrink-0">
          <button
            type="button"
            onClick={handleRefresh}
            className="flex items-center text-xs font-semibold text-slate-600 bg-white hover:bg-slate-50 border border-slate-200 px-3 py-2 rounded-xl transition-all shadow-xs cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
            새로고침
          </button>

          <button
            type="button"
            onClick={() => setIsEmailModalOpen(true)}
            className="relative flex items-center text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 px-3 py-2 rounded-xl transition-all shadow-xs cursor-pointer"
          >
            <Mail className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
            이메일 알림함
            {mail.unreadCount > 0 && (
              <span className="ml-1.5 bg-rose-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center">
                {mail.unreadCount}
              </span>
            )}
          </button>

          {user?.is_officer && (
            <button
              type="button"
              onClick={() => setIsOfficerStatsOpen(true)}
              className="flex items-center text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 px-3 py-2 rounded-xl transition-all shadow-xs cursor-pointer"
            >
              <BarChart3 className="w-3.5 h-3.5 mr-1.5" />
              담당자별 실적 통계
            </button>
          )}

          <button
            type="button"
            onClick={() => setIsModalOpen(true)}
            className="flex items-center text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-xl transition-all shadow-xs cursor-pointer"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            문의 등록
          </button>
        </div>
      </div>

      {/* KPI Stats Cards */}
      <DashboardStats
        stats={dash.stats}
        selectedStatus={dash.statusFilter}
        onSelectStatus={dash.handleStatsCardClick}
      />

      {/* 2-Tier Filter & Search Bar */}
      <DashboardFilterBar
        isOfficer={Boolean(user?.is_officer)}
        activeTab={dash.activeTab}
        onTabChange={dash.setActiveTab}
        search={dash.search}
        onSearchChange={dash.setSearch}
        isOverdueOnly={dash.isOverdueOnly}
        onToggleOverdue={() => dash.setIsOverdueOnly(!dash.isOverdueOnly)}
        assignedToMe={dash.assignedToMe}
        onToggleAssignedToMe={() => dash.setAssignedToMe(!dash.assignedToMe)}
        statusFilter={dash.statusFilter}
        onStatusChange={dash.setStatusFilter}
        categoryFilter={dash.categoryFilter}
        onCategoryChange={dash.setCategoryFilter}
        priorityFilter={dash.priorityFilter}
        onPriorityChange={dash.setPriorityFilter}
        sortBy={dash.sortBy}
        onSortByChange={dash.setSortBy}
        hasActiveFilters={dash.hasActiveFilters}
        onResetFilters={dash.resetFilters}
      />

      {/* Content Body: Tickets Grid vs FAQ Accordion */}
      {dash.activeTab === 'faq' ? (
        <FaqAccordion
          tickets={dash.tickets}
          onSelectTicket={(ticketId: number) => setSelectedTicketId(ticketId)}
        />
      ) : (
        <>
          {dash.loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-white rounded-xl border border-slate-200 p-5 h-44 animate-pulse">
                  <div className="h-4 bg-slate-100 rounded w-1/3 mb-4"></div>
                  <div className="h-6 bg-slate-100 rounded w-3/4 mb-3"></div>
                  <div className="h-3 bg-slate-100 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : dash.error ? (
            <div className="text-center py-12 bg-white rounded-2xl border border-rose-200">
              <p className="text-rose-600 font-medium text-sm">{dash.error}</p>
              <button
                type="button"
                onClick={dash.refreshAll}
                className="mt-3 text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 px-3 py-1.5 rounded-lg cursor-pointer"
              >
                다시 시도
              </button>
            </div>
          ) : dash.tickets.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-2xl border border-slate-200 shadow-xs">
              <Inbox className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <h3 className="text-base font-bold text-slate-700 mb-1">티켓이 없습니다</h3>
              <p className="text-xs text-slate-400 mb-4">
                {dash.hasActiveFilters
                  ? '설정된 필터 조건에 부합하는 티켓이 없습니다. 필터를 초기화해 보세요.'
                  : '등록된 문의가 없습니다. 새로운 문의를 등록해 보세요.'}
              </p>
              {dash.hasActiveFilters && (
                <button
                  type="button"
                  onClick={dash.resetFilters}
                  className="text-xs font-semibold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 px-3.5 py-1.5 rounded-lg cursor-pointer"
                >
                  필터 초기화
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {dash.tickets.map((ticket: Ticket) => (
                <TicketCard
                  key={ticket.id}
                  ticket={ticket}
                  onClick={(t) => setSelectedTicketId(t.id)}
                />
              ))}
            </div>
          )}

          {/* Pagination */}
          <DashboardPagination
            page={dash.page}
            total={dash.total}
            pageSize={dash.pageSize}
            onPageChange={dash.setPage}
          />
        </>
      )}

      {/* Modals */}
      <TicketCreateModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={handleRefresh}
        onSelectTicket={(ticketId: number) => {
          setIsModalOpen(false);
          setSelectedTicketId(ticketId);
        }}
      />

      <TicketDetailModal
        isOpen={Boolean(selectedTicketId)}
        ticketId={selectedTicketId}
        onClose={() => setSelectedTicketId(null)}
        onSuccess={handleRefresh}
        onSelectTicket={(ticketId: number) => setSelectedTicketId(ticketId)}
      />

      <OfficerStatsModal
        isOpen={isOfficerStatsOpen}
        onClose={() => setIsOfficerStatsOpen(false)}
      />

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
        onSelectTicket={(ticketId: number) => {
          setIsEmailModalOpen(false);
          setSelectedTicketId(ticketId);
        }}
      />
    </div>
  );
};
