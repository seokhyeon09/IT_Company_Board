import React, { useState } from 'react';
import { Loader2, UserCheck, Play, Lock } from 'lucide-react';
import { OfficerSimpleItem } from '../../ticket/types/ticket';
import { BulkActionType, BulkPanelMode } from '../types/bulk';
import { formatShortMonthDay } from '../../../shared/utils/absenceUtils';

interface BulkActionSubPanelProps {
  panelMode: BulkPanelMode;
  selectedCount: number;
  officers: OfficerSimpleItem[];
  submitting: boolean;
  onExecute: (params: {
    action: BulkActionType;
    officerId?: number | '';
    reason?: string;
    note?: string;
  }) => void;
  onCancel: () => void;
}

export const BulkActionSubPanel: React.FC<BulkActionSubPanelProps> = ({
  panelMode,
  selectedCount,
  officers,
  submitting,
  onExecute,
  onCancel,
}) => {
  const [officerId, setOfficerId] = useState<number | ''>('');
  const [reason, setReason] = useState('');
  const [closeNote, setCloseNote] = useState('');

  if (!panelMode) return null;

  const selectedOfficer = officers.find((o) => o.id === officerId);

  if (panelMode === 'assign') {
    return (
      <div className="p-3 bg-emerald-50/70 border border-emerald-200 rounded-xl space-y-2.5">
        <div className="flex items-center justify-between text-xs font-bold text-slate-800">
          <span>선택한 {selectedCount}건 담당자 지정/인계</span>
          <button type="button" onClick={onCancel} className="text-slate-500 hover:text-slate-700 cursor-pointer">
            닫기
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              담당 IT 직원 선택 *
            </label>
            <select
              value={officerId}
              onChange={(e) => setOfficerId(e.target.value ? Number(e.target.value) : '')}
              className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="">담당자를 선택하세요</option>
              {officers.map((officer) => (
                <option key={officer.id} value={officer.id}>
                  {officer.name} ({officer.login}){officer.is_absent ? ' [부재중]' : ''}
                </option>
              ))}
            </select>
            {selectedOfficer?.is_absent && (
              <p className="mt-1 text-[11px] text-amber-700 font-medium">
                선택한 담당자는 부재 중입니다
                {selectedOfficer.absent_until
                  ? `(~${formatShortMonthDay(selectedOfficer.absent_until)})`
                  : ''}
                . 인계는 가능하지만 처리가 지연될 수 있습니다.
              </p>
            )}
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              인계 사유 (선택)
            </label>
            <input
              type="text"
              maxLength={500}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="예: 담당자 변경, 업무 재분배"
              className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
          >
            취소
          </button>
          <button
            type="button"
            disabled={!officerId || submitting}
            onClick={() => onExecute({ action: 'assign', officerId, reason })}
            className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg disabled:opacity-50 cursor-pointer"
          >
            {submitting ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> : <UserCheck className="w-3.5 h-3.5 mr-1" />}
            일괄 인계 실행
          </button>
        </div>
      </div>
    );
  }

  if (panelMode === 'start_progress') {
    return (
      <div className="p-3 bg-indigo-50/70 border border-indigo-200 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <span className="text-xs font-semibold text-indigo-900">
          선택한 {selectedCount}건의 문의를 처리 중 상태로 변경할까요?
        </span>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
          >
            취소
          </button>
          <button
            type="button"
            disabled={submitting}
            onClick={() => onExecute({ action: 'start_progress' })}
            className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50 cursor-pointer"
          >
            {submitting ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> : <Play className="w-3.5 h-3.5 mr-1" />}
            처리 시작 실행
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-3 bg-rose-50/70 border border-rose-200 rounded-xl space-y-2.5">
      <div className="flex items-center justify-between text-xs font-bold text-rose-900">
        <span>선택한 {selectedCount}건을 직권 종결할까요? 종결 후에는 되돌릴 수 없습니다.</span>
        <button type="button" onClick={onCancel} className="text-slate-500 hover:text-slate-700 cursor-pointer">
          닫기
        </button>
      </div>
      <input
        type="text"
        maxLength={2000}
        value={closeNote}
        onChange={(e) => setCloseNote(e.target.value)}
        placeholder="종결 메모 (선택, 미입력 시 기존 조치 내용 또는 기본 사유가 기록됩니다)"
        className="w-full px-2.5 py-1.5 text-xs border border-rose-200 rounded-lg bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-rose-400"
      />
      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
        >
          취소
        </button>
        <button
          type="button"
          disabled={submitting}
          onClick={() => onExecute({ action: 'close', note: closeNote })}
          className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 rounded-lg disabled:opacity-50 cursor-pointer"
        >
          {submitting ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> : <Lock className="w-3.5 h-3.5 mr-1" />}
          직권 종결 확정
        </button>
      </div>
    </div>
  );
};
