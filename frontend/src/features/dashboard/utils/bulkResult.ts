import { BulkActionPayload, BulkActionResult, BulkActionType } from '../types/bulk';

export interface BulkFailureItem {
  id: number;
  label: string;
  message: string;
}

export function buildBulkPayload(params: {
  ticketIds: number[];
  action: BulkActionType;
  officerId?: number | '';
  reason?: string;
  note?: string;
}): BulkActionPayload {
  const payload: BulkActionPayload = {
    ticket_ids: params.ticketIds,
    action: params.action,
  };

  if (params.action === 'assign' && params.officerId) {
    payload.officer_id = Number(params.officerId);
  }

  const trimmedReason = params.reason?.trim();
  if ((params.action === 'assign' || params.action === 'assign_auto') && trimmedReason) {
    payload.reason = trimmedReason;
  }

  const trimmedNote = params.note?.trim();
  if (params.action === 'close' && trimmedNote) {
    payload.note = trimmedNote;
  }

  return payload;
}

export function formatBulkSummaryText(result: BulkActionResult): string {
  if (result.fail_count === 0) {
    return `총 ${result.total}건 중 ${result.success_count}건 처리 완료`;
  }
  return `총 ${result.total}건 중 ${result.success_count}건 성공, ${result.fail_count}건 실패`;
}

export function extractBulkFailures(result: BulkActionResult): BulkFailureItem[] {
  return result.results
    .filter((item) => !item.ok)
    .map((item) => ({
      id: item.id,
      label: item.ticket_number || `#${item.id}`,
      message: item.message,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'ko'));
}

export function chunkIds(ids: number[], chunkSize: number = 50): number[][] {
  if (chunkSize <= 0) return [ids];
  const chunks: number[][] = [];
  for (let i = 0; i < ids.length; i += chunkSize) {
    chunks.push(ids.slice(i, i + chunkSize));
  }
  return chunks;
}

export function aggregateBulkResults(
  action: BulkActionType,
  batches: BulkActionResult[]
): BulkActionResult {
  const results = batches.flatMap((b) => b.results);
  const successCount = results.filter((r) => r.ok).length;
  return {
    action,
    total: results.length,
    success_count: successCount,
    fail_count: results.length - successCount,
    results,
  };
}
