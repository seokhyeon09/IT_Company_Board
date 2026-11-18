export interface TicketStats {
  total: number;
  waiting: number;
  in_progress: number;
  pending: number;
  resolved: number;
  overdue: number;
}

export interface TicketListQueryParams {
  offset: number;
  limit: number;
  status?: string;
  category?: string;
  priority?: string;
  search?: string;
  is_overdue?: boolean;
  assigned_to_me?: boolean;
  sort_by?: string;
  is_faq?: boolean;
}

export type DashboardTab = 'all' | 'faq';

export type DashboardSortBy =
  | 'id desc'
  | 'id asc'
  | 'deadline asc'
  | 'priority desc'
  | 'write_date desc';

export const VALID_DASHBOARD_TABS: readonly DashboardTab[] = ['all', 'faq'];

export const VALID_DASHBOARD_SORTS: readonly DashboardSortBy[] = [
  'id desc',
  'id asc',
  'deadline asc',
  'priority desc',
  'write_date desc',
];

export interface DashboardQueryState {
  tab: DashboardTab;
  search: string;
  status: string;
  category: string;
  priority: string;
  sort: DashboardSortBy;
  overdue: boolean;
  mine: boolean;
  page: number;
}

export const DEFAULT_DASHBOARD_QUERY_STATE: DashboardQueryState = {
  tab: 'all',
  search: '',
  status: '',
  category: '',
  priority: '',
  sort: 'id desc',
  overdue: false,
  mine: false,
  page: 1,
};

export interface DashboardFilterValues {
  activeTab: DashboardTab;
  search: string;
  isOverdueOnly: boolean;
  assignedToMe: boolean;
  statusFilter: string;
  categoryFilter: string;
  priorityFilter: string;
  sortBy: string;
  hasActiveFilters: boolean;
}

export interface DashboardFilterHandlers {
  onTabChange: (tab: DashboardTab) => void;
  onSearchChange: (val: string) => void;
  onToggleOverdue: () => void;
  onToggleAssignedToMe: () => void;
  onStatusChange: (val: string) => void;
  onCategoryChange: (val: string) => void;
  onPriorityChange: (val: string) => void;
  onSortByChange: (val: string) => void;
  onResetFilters: () => void;
}

export interface OfficerStatItem {
  id: number;
  name: string;
  in_progress: number;
  resolved: number;
  closed: number;
  total_assigned: number;
  total_completed: number;
  categories: Record<string, number>;
  avg_resolution_hours?: number;
  resolved_measured_count?: number;
}

export interface CategoryStatItem {
  category: string;
  label: string;
  count: number;
  percentage: number;
  avg_resolution_hours?: number;
}

export interface OfficerStatsData {
  officers: OfficerStatItem[];
  category_breakdown?: CategoryStatItem[];
  overall_avg_resolution_hours?: number;
}
