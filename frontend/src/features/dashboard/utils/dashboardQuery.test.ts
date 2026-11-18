import { describe, it, expect } from 'vitest';
import {
  buildSearchWithTicketId,
  parseDashboardQuery,
  parseTicketIdFromSearch,
  serializeDashboardQuery,
} from './dashboardQuery';
import { DEFAULT_DASHBOARD_QUERY_STATE, DashboardQueryState } from '../types/dashboard';

describe('dashboardQuery (URL 쿼리 파싱/직렬화 및 ticket_id 공존)', () => {
  it('빈 쿼리 문자열은 기본 상태로 파싱된다', () => {
    expect(parseDashboardQuery('')).toEqual(DEFAULT_DASHBOARD_QUERY_STATE);
  });

  it('기본값과 동일한 필터는 직렬화 시 URL에서 생략된다', () => {
    expect(serializeDashboardQuery(DEFAULT_DASHBOARD_QUERY_STATE)).toBe('');
  });

  it('모든 필터와 페이지 상태가 직렬화/파싱 왕복 변환된다', () => {
    const state: DashboardQueryState = {
      tab: 'faq',
      search: 'VPN 접속',
      status: 'in_progress',
      category: 'network',
      priority: '3',
      sort: 'deadline asc',
      overdue: true,
      mine: true,
      page: 4,
    };

    const serialized = serializeDashboardQuery(state);
    expect(serialized).toContain('tab=faq');
    expect(serialized).toContain('q=VPN');
    expect(serialized).toContain('status=in_progress');
    expect(serialized).toContain('category=network');
    expect(serialized).toContain('priority=3');
    expect(serialized).toContain('sort=deadline+asc');
    expect(serialized).toContain('overdue=1');
    expect(serialized).toContain('mine=1');
    expect(serialized).toContain('page=4');

    expect(parseDashboardQuery(serialized)).toEqual(state);
  });

  it('잘못된 쿼리 값은 무시하고 기본값으로 대체한다', () => {
    const parsed = parseDashboardQuery(
      '?tab=invalid&status=unknown&category=food&priority=9&sort=hack&overdue=true&mine=yes&page=abc'
    );
    expect(parsed).toEqual(DEFAULT_DASHBOARD_QUERY_STATE);

    const negativePage = parseDashboardQuery('?page=-3');
    expect(negativePage.page).toBe(1);

    const zeroPage = parseDashboardQuery('?page=0');
    expect(zeroPage.page).toBe(1);
  });

  it('대시보드 필터 직렬화 시 기존 ticket_id 쿼리를 보존한다', () => {
    const nextSearch = serializeDashboardQuery(
      { ...DEFAULT_DASHBOARD_QUERY_STATE, status: 'pending', page: 2 },
      '?ticket_id=123&status=submitted'
    );
    const params = new URLSearchParams(nextSearch);
    expect(params.get('ticket_id')).toBe('123');
    expect(params.get('status')).toBe('pending');
    expect(params.get('page')).toBe('2');
  });

  it('필터 초기화 후 직렬화해도 ticket_id는 지워지지 않는다', () => {
    const nextSearch = serializeDashboardQuery(
      DEFAULT_DASHBOARD_QUERY_STATE,
      '?ticket_id=456&status=resolved&page=3'
    );
    expect(nextSearch).toBe('?ticket_id=456');
  });

  it('parseTicketIdFromSearch는 양의 정수만 허용한다', () => {
    expect(parseTicketIdFromSearch('?ticket_id=123')).toBe(123);
    expect(parseTicketIdFromSearch('?tab=faq&ticket_id=7')).toBe(7);
    expect(parseTicketIdFromSearch('?ticket_id=0')).toBeNull();
    expect(parseTicketIdFromSearch('?ticket_id=-5')).toBeNull();
    expect(parseTicketIdFromSearch('?ticket_id=1.5')).toBeNull();
    expect(parseTicketIdFromSearch('?ticket_id=abc')).toBeNull();
    expect(parseTicketIdFromSearch('?ticket_id=12abc')).toBeNull();
    expect(parseTicketIdFromSearch('')).toBeNull();
  });

  it('buildSearchWithTicketId는 필터 쿼리를 보존하면서 ticket_id만 추가/제거한다', () => {
    const added = buildSearchWithTicketId('?status=in_progress&page=2', 99);
    const addedParams = new URLSearchParams(added);
    expect(addedParams.get('status')).toBe('in_progress');
    expect(addedParams.get('page')).toBe('2');
    expect(addedParams.get('ticket_id')).toBe('99');

    const removed = buildSearchWithTicketId(added, null);
    const removedParams = new URLSearchParams(removed);
    expect(removedParams.get('ticket_id')).toBeNull();
    expect(removedParams.get('status')).toBe('in_progress');
    expect(removedParams.get('page')).toBe('2');
  });
});
