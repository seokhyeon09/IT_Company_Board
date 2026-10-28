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
  isOverdueOnly?: boolean;
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
}

export interface OfficerStatsData {
  officers: OfficerStatItem[];
}
