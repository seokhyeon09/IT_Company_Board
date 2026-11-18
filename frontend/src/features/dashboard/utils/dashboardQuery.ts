import {
  VALID_TICKET_CATEGORIES,
  VALID_TICKET_PRIORITIES,
  VALID_TICKET_STATUS_FILTERS,
} from '../../../shared/types/common';
import {
  DEFAULT_DASHBOARD_QUERY_STATE,
  DashboardQueryState,
  DashboardSortBy,
  VALID_DASHBOARD_SORTS,
} from '../types/dashboard';

const MANAGED_FILTER_KEYS = [
  'tab',
  'q',
  'status',
  'category',
  'priority',
  'sort',
  'overdue',
  'mine',
  'page',
] as const;

export function parsePositiveInt(raw: string | null): number | null {
  if (!raw) return null;
  const trimmed = raw.trim();
  if (!/^[1-9]\d*$/.test(trimmed)) return null;
  const parsed = Number(trimmed);
  return Number.isSafeInteger(parsed) && parsed > 0 ? parsed : null;
}

export function parseTicketIdFromSearch(searchStr: string): number | null {
  const params = new URLSearchParams(searchStr);
  return parsePositiveInt(params.get('ticket_id'));
}

export function buildSearchWithTicketId(currentSearch: string, ticketId: number | null): string {
  const params = new URLSearchParams(currentSearch);
  if (ticketId !== null && Number.isSafeInteger(ticketId) && ticketId > 0) {
    params.set('ticket_id', String(ticketId));
  } else {
    params.delete('ticket_id');
  }
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

function pickValidValue<T extends string>(
  raw: string | null,
  allowed: readonly T[],
  fallback: T | ''
): T | '' {
  if (!raw) return fallback;
  return (allowed as readonly string[]).includes(raw) ? (raw as T) : fallback;
}

export function parseDashboardQuery(searchStr: string): DashboardQueryState {
  const params = new URLSearchParams(searchStr);

  const tab = params.get('tab') === 'faq' ? 'faq' : DEFAULT_DASHBOARD_QUERY_STATE.tab;
  const search = params.get('q')?.trim() || DEFAULT_DASHBOARD_QUERY_STATE.search;
  const status = pickValidValue(params.get('status'), VALID_TICKET_STATUS_FILTERS, '');
  const category = pickValidValue(params.get('category'), VALID_TICKET_CATEGORIES, '');
  const priority = pickValidValue(params.get('priority'), VALID_TICKET_PRIORITIES, '');
  const rawSort = params.get('sort');
  const sort: DashboardSortBy =
    rawSort && (VALID_DASHBOARD_SORTS as readonly string[]).includes(rawSort)
      ? (rawSort as DashboardSortBy)
      : DEFAULT_DASHBOARD_QUERY_STATE.sort;
  const overdue = params.get('overdue') === '1';
  const mine = params.get('mine') === '1';
  const page = parsePositiveInt(params.get('page')) ?? DEFAULT_DASHBOARD_QUERY_STATE.page;

  return {
    tab,
    search,
    status,
    category,
    priority,
    sort,
    overdue,
    mine,
    page,
  };
}

export function serializeDashboardQuery(
  state: DashboardQueryState,
  currentSearch: string = ''
): string {
  const params = new URLSearchParams(currentSearch);
  for (const key of MANAGED_FILTER_KEYS) {
    params.delete(key);
  }

  if (state.tab === 'faq') {
    params.set('tab', 'faq');
  }

  const trimmedSearch = state.search.trim();
  if (trimmedSearch) {
    params.set('q', trimmedSearch);
  }

  if (state.status && (VALID_TICKET_STATUS_FILTERS as readonly string[]).includes(state.status)) {
    params.set('status', state.status);
  }

  if (state.category && (VALID_TICKET_CATEGORIES as readonly string[]).includes(state.category)) {
    params.set('category', state.category);
  }

  if (state.priority && (VALID_TICKET_PRIORITIES as readonly string[]).includes(state.priority)) {
    params.set('priority', state.priority);
  }

  if (
    state.sort &&
    state.sort !== DEFAULT_DASHBOARD_QUERY_STATE.sort &&
    (VALID_DASHBOARD_SORTS as readonly string[]).includes(state.sort)
  ) {
    params.set('sort', state.sort);
  }

  if (state.overdue) {
    params.set('overdue', '1');
  }

  if (state.mine) {
    params.set('mine', '1');
  }

  if (Number.isSafeInteger(state.page) && state.page > 1) {
    params.set('page', String(state.page));
  }

  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

export function replaceUrlSearch(nextSearch: string): void {
  if (typeof window === 'undefined') return;
  if (nextSearch === window.location.search) return;
  const nextUrl = `${window.location.pathname}${nextSearch}${window.location.hash}`;
  window.history.replaceState(null, '', nextUrl);
}
