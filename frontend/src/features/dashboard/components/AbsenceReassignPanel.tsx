import React, { useState } from 'react';
import { Loader2, Sparkles, UserCheck } from 'lucide-react';
import { OfficerSimpleItem } from '../../ticket/types/ticket';
import { AbsenceOpenTicket } from '../types/officer';
import { BulkActionResult } from '../types/bulk';
import { extractBulkFailures, formatBulkSummaryText } from '../utils/bulkResult';

export interface AbsenceReassignState {
  reassigning: boolean;
  error: string;
  result: BulkActionResult | null;
  onReassign: (mode: 'assign_auto' | 'assign', officerId?: number | '') => void;
  onDismiss: () => void;
}

interface AbsenceReassignPanelProps {
  openTickets: AbsenceOpenTicket[];
  openTicketTotal: number;
  officers: OfficerSimpleItem[];
  state: AbsenceReassignState;
}

export const AbsenceReassignPanel: React.FC<AbsenceReassignPanelProps> = ({
  openTickets,
  openTicketTotal,
  officers,
  state,
}) => {
  const [selectedOfficerId, setSelectedOfficerId] = useState<number | ''>('');

  if (state.result) {
    const failures = extractBulkFailures(state.result);
    return (
      <div className="space-y-2.5">
        <div className="text-xs font-bold text-slate-900">부재 연계 인계 결과</div>
        <div
          className={`p-2.5 rounded-lg border text-xs ${
            failures.length > 0
              ? 'bg-amber-50 border-amber-200 text-amber-900'
              : 'bg-emerald-50 border-emerald-200 text-emerald-900'
          }`}
        >
          <p className="font-semibold">{formatBulkSummaryText(state.result)}</p>
          {failures.length > 0 && (
            <ul className="mt-1.5 space-y-1 pl-4 list-disc text-[11px] text-rose-700 max-h-24 overflow-y-auto">
              {failures.map((f) => (
                <li key={f.id}>
                  <span className="font-mono font-semibold">{f.label}</span>: {f.message}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="flex justify-end">
          <button
            type="button"
            onClick={state.onDismiss}
            className="px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
          >
            확인
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2.5">
      <div className="text-xs font-bold text-slate-900">부재 설정 완료 - 미처리 문의 인계</div>
      <p className="text-xs text-slate-700 leading-relaxed">
        내게 배정된 미처리 문의 <strong className="text-amber-700">{openTickets.length}건</strong>이 있습니다. 다른 담당자에게 인계할까요?
      </p>
      {openTicketTotal > openTickets.length && (
        <p className="text-[11px] text-amber-700 font-medium">
          일부만 표시됩니다(총 {openTicketTotal}건)
        </p>
      )}

      <div className="max-h-24 overflow-y-auto bg-slate-50 border border-slate-200 rounded-lg p-2 space-y-1 text-[11px] text-slate-600">
        {openTickets.map((t) => (
          <div key={t.id} className="truncate">
            <span className="font-mono font-semibold text-slate-700">{t.ticket_number}</span>{' '}
            {t.title}
          </div>
        ))}
      </div>

      <button
        type="button"
        disabled={state.reassigning}
        onClick={() => state.onReassign('assign_auto')}
        className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50 cursor-pointer"
      >
        {state.reassigning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
        자동 배정(분야별 담당자, 부재자 제외)
      </button>

      <div className="pt-1 border-t border-slate-100 space-y-1.5">
        <label className="block text-[11px] font-semibold text-slate-600">
          담당자 직접 선택
        </label>
        <div className="flex gap-1.5">
          <select
            value={selectedOfficerId}
            onChange={(e) => setSelectedOfficerId(e.target.value ? Number(e.target.value) : '')}
            className="flex-1 min-w-0 px-2 py-1.5 text-xs border border-slate-300 rounded-lg bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500"
          >
            <option value="">담당자 선택</option>
            {officers.map((officer) => (
              <option key={officer.id} value={officer.id}>
                {officer.name} ({officer.login}){officer.is_absent ? ' [부재중]' : ''}
              </option>
            ))}
          </select>
          <button
            type="button"
            disabled={!selectedOfficerId || state.reassigning}
            onClick={() => state.onReassign('assign', selectedOfficerId)}
            className="inline-flex items-center px-2.5 py-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 rounded-lg disabled:opacity-50 cursor-pointer shrink-0"
          >
            <UserCheck className="w-3.5 h-3.5 mr-1" />
            인계
          </button>
        </div>
      </div>

      {state.error && <p className="text-xs text-rose-600 font-medium">{state.error}</p>}

      <div className="flex justify-end pt-1">
        <button
          type="button"
          disabled={state.reassigning}
          onClick={state.onDismiss}
          className="px-2.5 py-1 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
        >
          나중에 처리
        </button>
      </div>
    </div>
  );
};
