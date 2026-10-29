import { useState, useEffect, useCallback } from 'react';
import { ticketApi } from '../../../api/ticketApi';
import { getErrorMessage } from '../../../api/client';
import { Ticket } from '../../ticket/types/ticket';
import { TicketStats } from '../types/dashboard';

const PAGE_SIZE = 12;

export function useDashboardTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<TicketStats | null>(null);

  // Filters
  const [activeTab, setActiveTab] = useState<'all' | 'faq'>('all');
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [sortBy, setSortBy] = useState('id desc');
  const [isOverdueOnly, setIsOverdueOnly] = useState(false);
  const [assignedToMe, setAssignedToMe] = useState(false);

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
  const fetchStats = useCallback(async () => {
    try {
      const data = await ticketApi.getStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch ticket stats:', err);
    }
  }, []);

  // Fetch Tickets List
  const fetchTickets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = {
        offset: (page - 1) * PAGE_SIZE,
        limit: PAGE_SIZE,
      };

      if (debouncedSearch.trim()) {
        params.search = debouncedSearch.trim();
        params.searchQuery = debouncedSearch.trim();
      }
      if (statusFilter) {
        params.status = statusFilter;
        params.statusFilter = statusFilter;
      }
      if (categoryFilter) {
        params.category = categoryFilter;
        params.categoryFilter = categoryFilter;
      }
      if (priorityFilter) {
        params.priority = priorityFilter;
        params.priorityFilter = priorityFilter;
      }
      if (isOverdueOnly) {
        params.is_overdue = true;
        params.isOverdueOnly = true;
      }
      if (assignedToMe) {
        params.assigned_to_me = true;
        params.assignedToMe = true;
      }
      if (sortBy) {
        params.sort_by = sortBy;
        params.sortBy = sortBy;
      }
      if (activeTab === 'faq') {
        params.is_faq = true;
        params.isFaq = true;
      }

      const res = await ticketApi.getTickets(params);
      setTickets(res.tickets || (res as any).data || []);
      setTotal(res.total || 0);
    } catch (err: any) {
      setError(getErrorMessage(err, '티켓 목록을 불러오지 못했습니다.'));
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearch, statusFilter, categoryFilter, priorityFilter, isOverdueOnly, assignedToMe, sortBy, activeTab]);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

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
    setAssignedToMe(false);
    setSortBy('id desc');
    setActiveTab('all');
    setPage(1);
  };

  const hasActiveFilters = Boolean(
    search || statusFilter || categoryFilter || priorityFilter || isOverdueOnly || assignedToMe || activeTab !== 'all'
  );

  return {
    tickets,
    total,
    loading,
    error,
    stats,
    page,
    setPage,
    pageSize: PAGE_SIZE,
    activeTab,
    setActiveTab,
    search,
    setSearch,
    statusFilter,
    setStatusFilter,
    categoryFilter,
    setCategoryFilter,
    priorityFilter,
    setPriorityFilter,
    sortBy,
    setSortBy,
    isOverdueOnly,
    setIsOverdueOnly,
    assignedToMe,
    setAssignedToMe,
    handleStatsCardClick,
    resetFilters,
    hasActiveFilters,
    refreshAll: () => {
      fetchStats();
      fetchTickets();
    },
  };
}
