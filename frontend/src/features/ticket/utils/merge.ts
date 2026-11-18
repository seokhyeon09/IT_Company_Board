export const MERGEABLE_STATUSES = ['submitted', 'assigned', 'in_progress', 'pending'] as const;
export const MAX_MERGE_REASON_LENGTH = 500;

export function canMergeTicket(ticket: {
  status: string;
  merged_into_id?: number | null;
}): boolean {
  if (ticket.merged_into_id) {
    return false;
  }
  return (MERGEABLE_STATUSES as readonly string[]).includes(ticket.status);
}

export function formatSimilarityPercent(score: number): string {
  if (!Number.isFinite(score)) {
    return '0%';
  }
  const clamped = Math.max(0, Math.min(1, score));
  return `${Math.round(clamped * 100)}%`;
}

export function buildMergeConfirmMessage(targetNumber: string): string {
  return `이 문의를 ${targetNumber}에 병합합니다. 병합하면 이 문의는 취소 상태가 되며 되돌릴 수 없습니다.`;
}

export function validateMergeReason(reason: string): {
  valid: boolean;
  trimmed: string;
  error: string;
} {
  const trimmed = reason.trim();
  if (trimmed.length > MAX_MERGE_REASON_LENGTH) {
    return {
      valid: false,
      trimmed,
      error: '병합 사유는 최대 500자까지 입력할 수 있습니다.',
    };
  }
  return {
    valid: true,
    trimmed,
    error: '',
  };
}
