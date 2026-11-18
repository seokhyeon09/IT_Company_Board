import React from 'react';
import { GitMerge, Loader2, RefreshCw } from 'lucide-react';
import { statusMap } from '../../../../shared/types/common';
import { TicketDetail } from '../../types/ticket';
import { useMergeCandidates, useMergeExecution } from '../../hooks/useMergePanel';
import {
  MAX_MERGE_REASON_LENGTH,
  buildMergeConfirmMessage,
  canMergeTicket,
  formatSimilarityPercent,
} from '../../utils/merge';
import { InlineErrorNotice } from './InlineErrorNotice';

interface MergePanelProps {
  ticket: TicketDetail;
  isOfficer: boolean;
  onMerged?: () => void;
  onSelectTicket?: (ticketId: number) => void;
}

export const MergePanel: React.FC<MergePanelProps> = ({
  ticket,
  isOfficer,
  onMerged,
  onSelectTicket,
}) => {
  const canMerge = isOfficer && canMergeTicket(ticket);
  const { candidates, loading, error: candidatesError, reloadCandidates } = useMergeCandidates(
    ticket.id,
    canMerge
  );
  const exec = useMergeExecution(ticket.id, ticket.write_date, onMerged);
  const mergedList = isOfficer ? ticket.merged_tickets || [] : [];

  if (!ticket.merged_into_number && !canMerge && mergedList.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      {ticket.merged_into_number && (
        <div
          role="status"
          className="p-3.5 bg-slate-100 border border-slate-200 rounded-xl flex items-center space-x-2.5 text-xs text-slate-700"
        >
          <GitMerge className="w-4 h-4 text-slate-600 shrink-0" />
          <span className="font-semibold">
            이 문의는 {ticket.merged_into_number} 문의로 병합되었습니다.
          </span>
        </div>
      )}

      {mergedList.length > 0 && (
        <div className="p-3.5 bg-indigo-50/50 border border-indigo-200 rounded-xl space-y-2">
          <div className="flex items-center space-x-1.5 text-xs font-bold text-indigo-900">
            <GitMerge className="w-4 h-4 text-indigo-600" />
            <span>병합된 중복 문의 {mergedList.length}건</span>
          </div>
          <div className="space-y-1.5 max-h-40 overflow-y-auto">
            {mergedList.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelectTicket?.(item.id)}
                className="w-full text-left px-3 py-2 bg-white border border-indigo-100 hover:border-indigo-300 rounded-lg text-xs flex items-center justify-between gap-2 transition-colors cursor-pointer"
              >
                <span className="truncate">
                  <span className="font-mono font-semibold text-indigo-700 mr-2">
                    {item.ticket_number}
                  </span>
                  <span className="text-slate-800">{item.title}</span>
                </span>
                <span className="text-[11px] text-slate-500 shrink-0">{item.author_name}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {canMerge && (
        <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1.5">
              <GitMerge className="w-4 h-4 text-slate-600" />
              <h4 className="text-xs font-bold text-slate-800">중복 문의 병합</h4>
            </div>
            <button
              type="button"
              onClick={reloadCandidates}
              disabled={loading}
              className="inline-flex items-center px-2.5 py-1 text-[11px] font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-100 rounded-lg disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={`w-3 h-3 mr-1 ${loading ? 'animate-spin' : ''}`} />
              후보 불러오기
            </button>
          </div>

          {candidatesError && <InlineErrorNotice title="후보 조회 실패" message={candidatesError} />}

          {loading ? (
            <div className="py-3 flex items-center justify-center text-xs text-slate-500">
              <Loader2 className="w-4 h-4 animate-spin mr-1.5" />
              유사한 문의를 찾는 중입니다...
            </div>
          ) : candidates.length === 0 && !candidatesError ? (
            <p className="text-xs text-slate-500">유사한 문의를 찾지 못했습니다.</p>
          ) : (
            <div className="space-y-1.5 max-h-48 overflow-y-auto">
              {candidates.map((cand) => {
                const isSelected = exec.selectedTarget?.id === cand.id;
                const statusLabel = statusMap[cand.status]?.label || cand.status;
                return (
                  <button
                    key={cand.id}
                    type="button"
                    onClick={() => exec.setSelectedTarget(cand)}
                    className={`w-full text-left p-2.5 rounded-lg border text-xs transition-colors cursor-pointer ${
                      isSelected
                        ? 'bg-indigo-50 border-indigo-400 ring-1 ring-indigo-300'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center space-x-2 min-w-0">
                        <span className="font-mono font-bold text-slate-700 shrink-0">
                          {cand.ticket_number}
                        </span>
                        <span className="font-semibold text-slate-900 truncate">{cand.title}</span>
                      </div>
                      <span className="text-[11px] font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-1.5 py-0.5 rounded shrink-0">
                        유사도 {formatSimilarityPercent(cand.score)}
                      </span>
                    </div>
                    <div className="mt-1 flex items-center space-x-2 text-[11px] text-slate-500">
                      <span>{statusLabel}</span>
                      <span>·</span>
                      <span>{cand.author_name}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}

          {exec.selectedTarget && (
            <div className="pt-2 border-t border-slate-200 space-y-2">
              <input
                type="text"
                maxLength={MAX_MERGE_REASON_LENGTH}
                value={exec.reason}
                onChange={(e) => exec.setReason(e.target.value)}
                placeholder="병합 사유를 입력하세요 (선택, 미입력 시 '중복 문의')"
                className="w-full px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />

              <InlineErrorNotice title="병합 실패" message={exec.error} />

              {!exec.confirming ? (
                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={exec.requestConfirm}
                    className="px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg cursor-pointer"
                  >
                    병합
                  </button>
                </div>
              ) : (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg space-y-2">
                  <p className="text-xs font-semibold text-rose-800">
                    {buildMergeConfirmMessage(exec.selectedTarget.ticket_number)}
                  </p>
                  <div className="flex justify-end space-x-2">
                    <button
                      type="button"
                      onClick={exec.cancelConfirm}
                      disabled={exec.submitting}
                      className="px-3 py-1 text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-100 rounded-lg cursor-pointer"
                    >
                      취소
                    </button>
                    <button
                      type="button"
                      onClick={exec.executeMerge}
                      disabled={exec.submitting}
                      className="inline-flex items-center px-3 py-1 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 rounded-lg disabled:opacity-50 cursor-pointer"
                    >
                      {exec.submitting && <Loader2 className="w-3 h-3 mr-1 animate-spin" />}
                      병합 확정
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
