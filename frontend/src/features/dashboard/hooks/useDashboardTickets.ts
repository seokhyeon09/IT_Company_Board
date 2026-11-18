import { useState, useEffect, useCallback, useRef } from 'react';
import { ticketApi } from '../../../api/ticketApi';
import { getErrorMessage } from '../../../api/client';
import { Ticket } from '../../ticket/types/ticket';
import {
  DashboardSortBy,
  DashboardTab,
  TicketListQueryParams,
  TicketStats,
  VALID_DASHBOARD_SORTS,
} from '../types/dashboard';
import {
  parseDashboardQuery,
  replaceUrlSearch,
  serializeDashboardQuery,
} from '../utils/dashboardQuery';

const PAGE_SIZE = 12;

export function useDashboardTickets() {
  const [initialQuery] = useState(() =>
    parseDashboardQuery(typeof window !== 'undefined' ? window.location.search : '')
  );

  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<TicketStats | null>(null);

  // Filters
  const [activeTab, setActiveTab] = useState<DashboardTab>(initialQuery.tab);
  const [search, setSearch] = useState(initialQuery.search);
  const [debouncedSearch, setDebouncedSearch] = useState(initialQuery.search);
  const [statusFilter, setStatusFilter] = useState(initialQuery.status);
  const [categoryFilter, setCategoryFilter] = useState(initialQuery.category);
  const [priorityFilter, setPriorityFilter] = useState(initialQuery.priority);
  const [sortBy, setSortByState] = useState<DashboardSortBy>(initialQuery.sort);
  const [isOverdueOnly, setIsOverdueOnly] = useState(initialQuery.overdue);
  const [assignedToMe, setAssignedToMe] = useState(initialQuery.mine);

  // Pagination
  const [page, setPage] = useState(initialQuery.page);

  const prevSearchRef = useRef(search);

  const setSortBy = useCallback((val: string) => {
    const nextSort: DashboardSortBy = (VALID_DASHBOARD_SORTS as readonly string[]).includes(val)
      ? (val as DashboardSortBy)
      : 'id desc';
    setSortByState(nextSort);
  }, []);

  // Debounce search input (300ms) without resetting URL-initialized page on first mount
  useEffect(() => {
    if (prevSearchRef.current === search) return;
    prevSearchRef.current = search;
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(handler);
  }, [search]);

  // Sync filter state to URL query (preserving ticket_id and other unrelated params)
  useEffect(() => {
    const nextSearch = serializeDashboardQuery(
      {
        tab: activeTab,
        search,
        status: statusFilter,
        category: categoryFilter,
        priority: priorityFilter,
        sort: sortBy,
        overdue: isOverdueOnly,
        mine: assignedToMe,
        page,
      },
      typeof window !== 'undefined' ? window.location.search : ''
    );
    replaceUrlSearch(nextSearch);
  }, [
    activeTab,
    search,
    statusFilter,
    categoryFilter,
    priorityFilter,
    sortBy,
    isOverdueOnly,
    assignedToMe,
    page,
  ]);

  // Fetch KPI Stats
  const fetchStats = useCallback(async () => {
    try {
      const data = await ticketApi.getStats();
      setStats((data as any)?.data || data);
    } catch (err) {
      console.error('Failed to fetch ticket stats:', err);
    }
  }, []);

  // Fetch Tickets List
  const fetchTickets = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const params: TicketListQueryParams = {
        offset: (page - 1) * PAGE_SIZE,
        limit: PAGE_SIZE,
      };

      if (debouncedSearch.trim()) params.search = debouncedSearch.trim();
      if (statusFilter) params.status = statusFilter;
      if (categoryFilter) params.category = categoryFilter;
      if (priorityFilter) params.priority = priorityFilter;
      if (isOverdueOnly) params.is_overdue = true;
      if (assignedToMe) params.assigned_to_me = true;
      if (sortBy) params.sort_by = sortBy;
      if (activeTab === 'faq') params.is_faq = true;

      const res = await ticketApi.getTickets(params, { signal });
      setTickets(res.tickets || (res as any).data || []);
      setTotal(res.total || 0);
    } catch (err: any) {
      if (err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') {
        return;
      }
      setError(getErrorMessage(err, '티켓 목록을 불러오지 못했습니다.'));
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearch, statusFilter, categoryFilter, priorityFilter, isOverdueOnly, assignedToMe, sortBy, activeTab]);

  useEffect(() => {
    const controller = new AbortController();
    fetchTickets(controller.signal);
    return () => {
      controller.abort();
    };
  }, [fetchTickets]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const handleStatsCardClick = (targetStatus: string) => {
    setActiveTab('all');
    setPage(1);
    setSortByState('id desc');
    if (targetStatus === '') {
      setStatusFilter('');
    } else {
      setStatusFilter((prev) => (prev === targetStatus ? '' : targetStatus));
    }
  };

  const resetFilters = () => {
    prevSearchRef.current = '';
    setSearch('');
    setDebouncedSearch('');
    setStatusFilter('');
    setCategoryFilter('');
    setPriorityFilter('');
    setIsOverdueOnly(false);
    setAssignedToMe(false);
    setSortByState('id desc');
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
