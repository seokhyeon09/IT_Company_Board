import { describe, it, expect } from 'vitest';
import {
  MAX_MERGE_REASON_LENGTH,
  buildMergeConfirmMessage,
  canMergeTicket,
  formatSimilarityPercent,
  validateMergeReason,
} from './merge';

describe('merge utils', () => {
  it('determines mergeable ticket statuses and excludes already merged tickets', () => {
    expect(canMergeTicket({ status: 'submitted', merged_into_id: null })).toBe(true);
    expect(canMergeTicket({ status: 'assigned', merged_into_id: null })).toBe(true);
    expect(canMergeTicket({ status: 'in_progress', merged_into_id: null })).toBe(true);
    expect(canMergeTicket({ status: 'pending', merged_into_id: null })).toBe(true);

    expect(canMergeTicket({ status: 'resolved', merged_into_id: null })).toBe(false);
    expect(canMergeTicket({ status: 'closed', merged_into_id: null })).toBe(false);
    expect(canMergeTicket({ status: 'canceled', merged_into_id: null })).toBe(false);
    expect(canMergeTicket({ status: 'in_progress', merged_into_id: 99 })).toBe(false);
  });

  it('formats similarity score as clamped percentage', () => {
    expect(formatSimilarityPercent(0.754)).toBe('75%');
    expect(formatSimilarityPercent(0.2)).toBe('20%');
    expect(formatSimilarityPercent(1.2)).toBe('100%');
    expect(formatSimilarityPercent(-0.1)).toBe('0%');
    expect(formatSimilarityPercent(Number.NaN)).toBe('0%');
  });

  it('builds Korean confirmation message with target ticket number', () => {
    expect(buildMergeConfirmMessage('TKT-2026-0042')).toBe(
      '이 문의를 TKT-2026-0042에 병합합니다. 병합하면 이 문의는 취소 상태가 되며 되돌릴 수 없습니다.'
    );
  });

  it('validates merge reason length while allowing empty reason', () => {
    expect(validateMergeReason('   ')).toEqual({ valid: true, trimmed: '', error: '' });
    expect(validateMergeReason('  중복 접수  ')).toEqual({
      valid: true,
      trimmed: '중복 접수',
      error: '',
    });
    const tooLong = '가'.repeat(MAX_MERGE_REASON_LENGTH + 1);
    expect(validateMergeReason(tooLong)).toEqual({
      valid: false,
      trimmed: tooLong,
      error: '병합 사유는 최대 500자까지 입력할 수 있습니다.',
    });
  });
});
