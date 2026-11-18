import { describe, it, expect } from 'vitest';
import { buildTicketExportParams, buildTicketListParams } from './listParams';
import { TicketFilterInput } from '../types/dashboard';

const baseFilters: TicketFilterInput = {
  search: '',
  status: '',
  category: '',
  priority: '',
  isOverdueOnly: false,
  assignedToMe: false,
  sortBy: '',
  activeTab: 'all',
};

describe('buildTicketListParams & buildTicketExportParams', () => {
  it('기본값 필드는 생략하고 offset/limit을 계산한다', () => {
    expect(
      buildTicketListParams({
        ...baseFilters,
        page: 1,
        pageSize: 12,
      })
    ).toEqual({
      offset: 0,
      limit: 12,
    });

    expect(
      buildTicketListParams({
        ...baseFilters,
        page: 3,
        pageSize: 12,
      })
    ).toEqual({
      offset: 24,
      limit: 12,
    });
  });

  it('검색어를 trim하고 공백만 있으면 생략한다', () => {
    expect(
      buildTicketExportParams({
        ...baseFilters,
        search: '   ',
      })
    ).toEqual({});

    expect(
      buildTicketExportParams({
        ...baseFilters,
        search: '  VPN 접속  ',
      })
    ).toEqual({
      search: 'VPN 접속',
    });
  });

  it('faq 탭과 모든 활성 필터를 snake_case 파라미터로 변환한다', () => {
    const result = buildTicketListParams({
      page: 2,
      pageSize: 12,
      search: '프린터',
      status: 'in_progress',
      category: 'hw',
      priority: '3',
      isOverdueOnly: true,
      assignedToMe: true,
      sortBy: 'deadline asc',
      activeTab: 'faq',
    });

    expect(result).toEqual({
      offset: 12,
      limit: 12,
      search: '프린터',
      status: 'in_progress',
      category: 'hw',
      priority: '3',
      is_overdue: true,
      assigned_to_me: true,
      sort_by: 'deadline asc',
      is_faq: true,
    });
  });

  it('buildTicketExportParams는 offset과 limit을 포함하지 않는다', () => {
    const exported = buildTicketExportParams({
      ...baseFilters,
      status: 'resolved',
      activeTab: 'faq',
      sortBy: 'id desc',
    });
    expect(exported).toEqual({
      status: 'resolved',
      sort_by: 'id desc',
      is_faq: true,
    });
    expect('offset' in exported).toBe(false);
    expect('limit' in exported).toBe(false);
  });
});
