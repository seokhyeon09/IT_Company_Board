import { describe, it, expect } from 'vitest';
import {
  aggregateBulkResults,
  buildBulkPayload,
  chunkIds,
  extractBulkFailures,
  formatBulkSummaryText,
} from './bulkResult';

describe('bulkResult utils', () => {
  it('builds bulk payloads according to action type', () => {
    expect(
      buildBulkPayload({
        ticketIds: [1, 2],
        action: 'assign',
        officerId: 5,
        reason: '  담당 변경  ',
        note: '무시되어야 함',
      })
    ).toEqual({
      ticket_ids: [1, 2],
      action: 'assign',
      officer_id: 5,
      reason: '담당 변경',
    });

    expect(
      buildBulkPayload({
        ticketIds: [3],
        action: 'close',
        note: '  직권 종결 메모  ',
      })
    ).toEqual({
      ticket_ids: [3],
      action: 'close',
      note: '직권 종결 메모',
    });

    expect(
      buildBulkPayload({
        ticketIds: [4],
        action: 'start_progress',
      })
    ).toEqual({
      ticket_ids: [4],
      action: 'start_progress',
    });
  });

  it('formats summary text and sorts failure items for display', () => {
    const allOk = {
      action: 'start_progress' as const,
      total: 3,
      success_count: 3,
      fail_count: 0,
      results: [],
    };
    expect(formatBulkSummaryText(allOk)).toBe('총 3건 중 3건 처리 완료');

    const partial = {
      action: 'close' as const,
      total: 3,
      success_count: 1,
      fail_count: 2,
      results: [
        { id: 20, ticket_number: 'TKT-20', ok: false, message: '상태 불가' },
        { id: 10, ticket_number: 'TKT-10', ok: true, message: '처리되었습니다.' },
        { id: 99, ticket_number: null, ok: false, message: '문의를 찾을 수 없습니다.' },
      ],
    };
    expect(formatBulkSummaryText(partial)).toBe('총 3건 중 1건 성공, 2건 실패');
    expect(extractBulkFailures(partial)).toEqual([
      { id: 99, label: '#99', message: '문의를 찾을 수 없습니다.' },
      { id: 20, label: 'TKT-20', message: '상태 불가' },
    ]);
  });

  it('chunks ids by 50 and aggregates batch results', () => {
    const ids = Array.from({ length: 105 }, (_, i) => i + 1);
    const chunks = chunkIds(ids, 50);
    expect(chunks.map((c) => c.length)).toEqual([50, 50, 5]);

    const agg = aggregateBulkResults('assign_auto', [
      {
        action: 'assign_auto',
        total: 2,
        success_count: 2,
        fail_count: 0,
        results: [
          { id: 1, ticket_number: 'TKT-1', ok: true, message: '처리되었습니다.' },
          { id: 2, ticket_number: 'TKT-2', ok: true, message: '처리되었습니다.' },
        ],
      },
      {
        action: 'assign_auto',
        total: 1,
        success_count: 0,
        fail_count: 1,
        results: [{ id: 3, ticket_number: 'TKT-3', ok: false, message: '후보 없음' }],
      },
    ]);
    expect(agg).toMatchObject({
      action: 'assign_auto',
      total: 3,
      success_count: 2,
      fail_count: 1,
    });
  });
});
