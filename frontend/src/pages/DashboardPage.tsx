import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useRefreshOnFocus } from '../shared/hooks/useRefreshOnFocus';
import { DashboardStats } from '../components/DashboardStats';
import { FaqAccordion } from '../components/FaqAccordion';
import { TicketDetailModal } from '../features/ticket/components/TicketDetailModal';
import { TicketCreateModal } from '../features/ticket/components/TicketCreateModal';
import { DashboardHeader } from '../features/dashboard/components/DashboardHeader';
import { DashboardFilterBar } from '../features/dashboard/components/DashboardFilterBar';
import { DashboardTicketList } from '../features/dashboard/components/DashboardTicketList';
import { BulkActionBar } from '../features/dashboard/components/BulkActionBar';
import { DashboardPagination } from '../features/dashboard/components/DashboardPagination';
import { OfficerStatsModal } from '../features/dashboard/components/OfficerStatsModal';
import { SlaReportModal } from '../features/dashboard/components/SlaReportModal';
import { EmailNotificationModal } from '../features/notification/components/EmailNotificationModal';
import { useEmailNotifications } from '../features/notification/hooks/useEmailNotifications';
import { useDashboardTickets } from '../features/dashboard/hooks/useDashboardTickets';
import { useTicketExport } from '../features/dashboard/hooks/useTicketExport';
import { useTicketSelection } from '../features/dashboard/hooks/useTicketSelection';
import { useBulkActions } from '../features/dashboard/hooks/useBulkActions';
import {
  buildSearchWithTicketId,
  parseTicketIdFromSearch,
  replaceUrlSearch,
} from '../features/dashboard/utils/dashboardQuery';

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const isOfficer = Boolean(user?.is_officer);
  const mail = useEmailNotifications(user?.uid);
  const dash = useDashboardTickets();
  const csvExport = useTicketExport(dash.exportParams);
  const selectionResetKey = `${dash.activeTab}|${dash.search}|${dash.statusFilter}|${dash.categoryFilter}|${dash.priorityFilter}|${dash.sortBy}|${dash.isOverdueOnly}|${dash.assignedToMe}|${dash.page}`;
  const selection = useTicketSelection(selectionResetKey);
  const bulk = useBulkActions({
    isOfficer,
    onSuccess: (res) => {
      selection.keepFailedOnly(res.results);
      dash.refreshAll();
    },
  });
  const pageTicketIds = dash.tickets.map((t) => t.id);

  // Modals & deep-link ticket_id state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(() =>
    parseTicketIdFromSearch(typeof window !== 'undefined' ? window.location.search : '')
  );
  const [isOfficerStatsOpen, setIsOfficerStatsOpen] = useState(false);
  const [isSlaReportOpen, setIsSlaReportOpen] = useState(false);
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);

  // Sync selectedTicketId to URL query (?ticket_id=...) without touching filter params
  useEffect(() => {
    const currentSearch = typeof window !== 'undefined' ? window.location.search : '';
    replaceUrlSearch(buildSearchWithTicketId(currentSearch, selectedTicketId));
  }, [selectedTicketId]);

  const { markRefreshed } = useRefreshOnFocus(dash.refreshAll);

  const handleRefresh = () => {
    markRefreshed();
    dash.refreshAll();
    mail.refresh();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <DashboardHeader
        user={user}
        unreadCount={mail.unreadCount}
        exportState={{
          exporting: csvExport.exporting,
          message: csvExport.message,
          error: csvExport.error,
          onExport: csvExport.exportCsv,
        }}
        onRefresh={handleRefresh}
        onOpenEmailModal={() => setIsEmailModalOpen(true)}
        onOpenOfficerStats={() => setIsOfficerStatsOpen(true)}
        onOpenSlaReport={() => setIsSlaReportOpen(true)}
        onOpenCreateModal={() => setIsModalOpen(true)}
      />

      <DashboardStats
        stats={dash.stats}
        selectedStatus={dash.statusFilter}
        onSelectStatus={dash.handleStatsCardClick}
      />

      <DashboardFilterBar
        isOfficer={Boolean(user?.is_officer)}
        filters={{
          activeTab: dash.activeTab,
          search: dash.search,
          isOverdueOnly: dash.isOverdueOnly,
          assignedToMe: dash.assignedToMe,
          statusFilter: dash.statusFilter,
          categoryFilter: dash.categoryFilter,
          priorityFilter: dash.priorityFilter,
          sortBy: dash.sortBy,
          hasActiveFilters: dash.hasActiveFilters,
        }}
        handlers={{
          onTabChange: dash.setActiveTab,
          onSearchChange: dash.setSearch,
          onToggleOverdue: () => dash.setIsOverdueOnly(!dash.isOverdueOnly),
          onToggleAssignedToMe: () => dash.setAssignedToMe(!dash.assignedToMe),
          onStatusChange: dash.setStatusFilter,
          onCategoryChange: dash.setCategoryFilter,
          onPriorityChange: dash.setPriorityFilter,
          onSortByChange: dash.setSortBy,
          onResetFilters: dash.resetFilters,
        }}
      />

      {dash.activeTab === 'faq' ? (
        <FaqAccordion
          tickets={dash.tickets}
          onSelectTicket={(ticketId: number) => setSelectedTicketId(ticketId)}
        />
      ) : (
        <>
          {isOfficer && (
            <BulkActionBar
              selectedIds={selection.selectedIds}
              pageTicketIds={pageTicketIds}
              officers={bulk.officers}
              state={{
                submitting: bulk.submitting,
                error: bulk.error,
                result: bulk.result,
                limitWarning: selection.limitWarning,
                onTogglePageAll: () => selection.togglePageAll(pageTicketIds),
                onClearSelection: selection.clearSelection,
                onExecuteBulk: bulk.executeBulk,
                onDismissResult: bulk.clearResult,
              }}
            />
          )}

          <DashboardTicketList
            loading={dash.loading}
            error={dash.error}
            tickets={dash.tickets}
            hasActiveFilters={dash.hasActiveFilters}
            onRetry={dash.refreshAll}
            onResetFilters={dash.resetFilters}
            onSelectTicket={(ticketId: number) => setSelectedTicketId(ticketId)}
            selection={
              isOfficer
                ? {
                    selectable: true,
                    selectedIds: selection.selectedIds,
                    onToggleSelect: selection.toggleTicket,
                  }
                : undefined
            }
          />

          <DashboardPagination
            page={dash.page}
            total={dash.total}
            pageSize={dash.pageSize}
            onPageChange={dash.setPage}
          />
        </>
      )}

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

      <SlaReportModal
        isOpen={isSlaReportOpen}
        onClose={() => setIsSlaReportOpen(false)}
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
