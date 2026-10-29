import { TicketCategory, TicketPriority, TicketStatusFilter } from '../../../shared/types/common';

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
  statusFilter?: TicketStatusFilter;
  categoryFilter?: TicketCategory | '';
  priorityFilter?: TicketPriority | '';
  searchQuery?: string;
  status?: string;
  category?: string;
  priority?: string;
  search?: string;
  isOverdueOnly?: boolean;
  assignedToMe?: boolean;
  sortBy?: string;
  isFaq?: boolean;
  is_overdue?: boolean;
  assigned_to_me?: boolean;
  sort_by?: string;
  is_faq?: boolean;
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
