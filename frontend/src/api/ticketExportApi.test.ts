import { describe, it, expect, vi, afterEach } from 'vitest';
import { apiClient, getErrorMessage } from './client';
import { ticketApi } from './ticketApi';

describe('ticketApi.exportTickets', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('필터 파라미터와 responseType blob으로 /tickets/export를 호출하고 헤더를 파싱한다', async () => {
    const mockBlob = new Blob(['id,title\n1,test'], { type: 'text/csv' });
    const getSpy = vi.spyOn(apiClient, 'get').mockResolvedValue({
      data: mockBlob,
      headers: {
        'content-disposition': 'attachment; filename="tickets_export.csv"',
        'x-export-truncated': 'true',
      },
    });

    const result = await ticketApi.exportTickets({
      category: 'hw',
      status: 'in_progress',
      is_overdue: true,
      search: '모니터',
    });

    expect(getSpy).toHaveBeenCalledWith('/tickets/export', {
      params: {
        category: 'hw',
        status: 'in_progress',
        is_overdue: true,
        search: '모니터',
      },
      responseType: 'blob',
    });
    expect(result.blob).toBe(mockBlob);
    expect(result.filename).toBe('tickets_export.csv');
    expect(result.truncated).toBe(true);
  });

  it('content-disposition 헤더가 없으면 기본 파일명을 생성한다', async () => {
    const mockBlob = new Blob(['id'], { type: 'text/csv' });
    vi.spyOn(apiClient, 'get').mockResolvedValue({
      data: mockBlob,
      headers: {},
    });

    const result = await ticketApi.exportTickets({});
    expect(result.filename).toMatch(/^tickets_\d{8}\.csv$/);
    expect(result.truncated).toBe(false);
  });

  it('에러 응답이 JSON Blob이면 파싱하여 getErrorMessage가 읽을 수 있게 변환한다', async () => {
    const errorBlob = {
      text: async () => JSON.stringify({ detail: '담당자만 내보낼 수 있습니다.' }),
    };
    const errorObj: any = {
      message: 'Request failed with status code 403',
      response: { status: 403, data: errorBlob },
    };
    vi.spyOn(apiClient, 'get').mockRejectedValue(errorObj);

    let caught: any;
    try {
      await ticketApi.exportTickets({});
    } catch (err) {
      caught = err;
    }

    expect(caught).toBeDefined();
    expect(getErrorMessage(caught, '실패')).toBe('담당자만 내보낼 수 있습니다.');
  });
});

describe('ticketApi.getOfficers', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('부재 상태 필드(is_absent, absent_until)를 유지한 채 담당자 목록을 반환한다', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue({
      data: {
        status: 'success',
        data: [
          { id: 2, name: '김담당', login: 'kim', is_absent: true, absent_until: '2026-12-01' },
          { id: 3, name: '이담당', login: 'lee', is_absent: false, absent_until: null },
        ],
      },
    });

    const res = await ticketApi.getOfficers();
    expect(res.officers).toEqual([
      { id: 2, name: '김담당', login: 'kim', is_absent: true, absent_until: '2026-12-01' },
      { id: 3, name: '이담당', login: 'lee', is_absent: false, absent_until: null },
    ]);
  });
});
