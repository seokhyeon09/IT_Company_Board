import {
  TicketExportQueryParams,
  TicketFilterInput,
  TicketListFilterInput,
  TicketListQueryParams,
} from '../types/dashboard';

export function buildTicketExportParams(input: TicketFilterInput): TicketExportQueryParams {
  const params: TicketExportQueryParams = {};
  const trimmedSearch = input.search.trim();

  if (trimmedSearch) params.search = trimmedSearch;
  if (input.status) params.status = input.status;
  if (input.category) params.category = input.category;
  if (input.priority) params.priority = input.priority;
  if (input.isOverdueOnly) params.is_overdue = true;
  if (input.assignedToMe) params.assigned_to_me = true;
  if (input.sortBy) params.sort_by = input.sortBy;
  if (input.activeTab === 'faq') params.is_faq = true;

  return params;
}

export function buildTicketListParams(input: TicketListFilterInput): TicketListQueryParams {
  const safePage = Math.max(1, input.page);
  return {
    offset: (safePage - 1) * input.pageSize,
    limit: input.pageSize,
    ...buildTicketExportParams(input),
  };
}
