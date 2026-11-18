import { describe, it, expect, vi, afterEach } from 'vitest';
import { apiClient } from './client';
import { ticketApi } from './ticketApi';
import type { Ticket } from '../features/ticket/types/ticket';
import type { TicketStats } from '../features/dashboard/types/dashboard';

const sampleTicket: Ticket = {
  id: 101,
  ticket_number: 'T-2026-0101',
  title: 'VPN 접속 불가',
  category: 'network',
  status: 'in_progress',
  priority: '3',
  is_overdue: false,
  is_faq: false,
};

const sampleStats: TicketStats = {
  total: 12,
  waiting: 3,
  in_progress: 4,
  pending: 1,
  resolved: 4,
  overdue: 2,
};

describe('ticketApi.getTickets', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('snake_case 필터 파라미터와 signal 옵션을 apiClient.get에 그대로 전달한다', async () => {
    const controller = new AbortController();
    const getSpy = vi.spyOn(apiClient, 'get').mockResolvedValue({
      data: { status: 'success', total: 1, data: [sampleTicket] },
    });

    await ticketApi.getTickets(
      {
        offset: 20,
        limit: 10,
        status: 'in_progress',
        category: 'network',
        priority: '3',
        search: 'VPN',
        is_overdue: true,
        assigned_to_me: true,
        sort_by: 'deadline asc',
        is_faq: true,
      },
      { signal: controller.signal }
    );

    expect(getSpy).toHaveBeenCalledTimes(1);
    expect(getSpy).toHaveBeenCalledWith('/tickets', {
      params: {
        offset: 20,
        limit: 10,
        status: 'in_progress',
        category: 'network',
        priority: '3',
        search: 'VPN',
        is_overdue: true,
        assigned_to_me: true,
        sort_by: 'deadline asc',
        is_faq: true,
      },
      signal: controller.signal,
    });
  });

  it('빈 문자열과 false 불리언 파라미터는 쿼리 객체에서 제외한다', async () => {
    const getSpy = vi.spyOn(apiClient, 'get').mockResolvedValue({
      data: { status: 'success', total: 0, data: [] },
    });

    await ticketApi.getTickets({
      offset: 0,
      limit: 20,
      status: '',
      category: '',
      priority: '',
      search: '',
      is_overdue: false,
      assigned_to_me: false,
      sort_by: '',
      is_faq: false,
    });

    expect(getSpy).toHaveBeenCalledWith('/tickets', {
      params: {
        offset: 0,
        limit: 20,
      },
    });
  });

  it('응답 구조를 { total, tickets } 형태로 정규화한다', async () => {
    const getSpy = vi.spyOn(apiClient, 'get');

    // { status, total, data } 형태
    getSpy.mockResolvedValueOnce({
      data: { status: 'success', total: 1, data: [sampleTicket] },
    });
    const wrapped = await ticketApi.getTickets({ offset: 0, limit: 20 });
    expect(wrapped).toEqual({ total: 1, tickets: [sampleTicket] });

    // { tickets } 폴백 형태
    getSpy.mockResolvedValueOnce({
      data: { total: 2, tickets: [sampleTicket] },
    });
    const fallback = await ticketApi.getTickets({ offset: 0, limit: 20 });
    expect(fallback).toEqual({ total: 2, tickets: [sampleTicket] });

    // 빈 응답 형태
    getSpy.mockResolvedValueOnce({ data: {} });
    const empty = await ticketApi.getTickets({ offset: 0, limit: 20 });
    expect(empty).toEqual({ total: 0, tickets: [] });

    // null 응답 형태
    getSpy.mockResolvedValueOnce({ data: null });
    const nullBody = await ticketApi.getTickets({ offset: 0, limit: 20 });
    expect(nullBody).toEqual({ total: 0, tickets: [] });
  });
});

describe('ticketApi.getStats', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('{ status, data } 래핑 응답을 언래핑하고 비래핑 응답도 그대로 반환한다', async () => {
    const getSpy = vi.spyOn(apiClient, 'get');

    getSpy.mockResolvedValueOnce({
      data: { status: 'success', data: sampleStats },
    });
    const wrappedStats = await ticketApi.getStats();
    expect(getSpy).toHaveBeenNthCalledWith(1, '/tickets/stats');
    expect(wrappedStats).toEqual(sampleStats);

    getSpy.mockResolvedValueOnce({
      data: sampleStats,
    });
    const directStats = await ticketApi.getStats();
    expect(getSpy).toHaveBeenNthCalledWith(2, '/tickets/stats');
    expect(directStats).toEqual(sampleStats);
  });
});
