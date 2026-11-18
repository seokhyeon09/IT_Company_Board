import React from 'react';
import { UserCheck, Loader2 } from 'lucide-react';
import { OfficerSimpleItem } from '../../../types/ticket';
import { formatShortMonthDay } from '../../../../../shared/utils/absenceUtils';

interface DesignateOfficerFormProps {
  isSubmitted: boolean;
  officers: OfficerSimpleItem[];
  selectedOfficerId: number | '';
  onSelectOfficer: (id: number | '') => void;
  assignReason: string;
  setAssignReason: (val: string) => void;
  submitting: boolean;
  error?: string | null;
  onCancel: () => void;
  onSubmit: () => void;
}

export const DesignateOfficerForm: React.FC<DesignateOfficerFormProps> = ({
  isSubmitted,
  officers,
  selectedOfficerId,
  onSelectOfficer,
  assignReason,
  setAssignReason,
  submitting,
  error,
  onCancel,
  onSubmit,
}) => {
  const isReassign = !isSubmitted;
  const selectedOfficer = officers.find((o) => o.id === selectedOfficerId);
  const canSubmit =
    Boolean(selectedOfficerId) &&
    (!isReassign || Boolean(assignReason.trim())) &&
    !submitting;

  return (
    <div className="p-3 bg-white border border-emerald-200 rounded-lg space-y-2.5 animate-in fade-in">
      <div className="text-xs font-bold text-slate-800 flex items-center justify-between">
        <span>{isSubmitted ? '담당자 신규 지정' : '담당자 인계 / 재지정'}</span>
        <button
          type="button"
          onClick={onCancel}
          className="text-slate-400 hover:text-slate-600 text-xs cursor-pointer"
        >
          닫기
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">
            담당 IT 직원 선택 *
          </label>
          <select
            value={selectedOfficerId}
            onChange={(e) => onSelectOfficer(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-800"
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

        {isReassign && (
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              인계 사유 *
            </label>
            <input
              type="text"
              value={assignReason}
              onChange={(e) => setAssignReason(e.target.value)}
              placeholder="예: 휴가 부재, 전문 분야 변경 등"
              className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-800"
            />
          </div>
        )}
      </div>

      {error && <p className="text-xs text-rose-600 font-medium">{error}</p>}

      <div className="flex justify-end space-x-2 pt-1">
        <button
          type="button"
          onClick={onCancel}
          className="px-2.5 py-1 text-xs text-slate-600 bg-white border border-slate-200 rounded-md hover:bg-slate-50 cursor-pointer"
        >
          취소
        </button>
        <button
          type="button"
          disabled={!canSubmit}
          onClick={onSubmit}
          className="flex items-center px-3 py-1 text-xs font-semibold text-white bg-emerald-600 rounded-md hover:bg-emerald-700 disabled:opacity-50 cursor-pointer shadow-xs"
        >
          {submitting ? (
            <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
          ) : (
            <UserCheck className="w-3.5 h-3.5 mr-1" />
          )}
          {isSubmitted ? '지정 확정' : '인계 확정'}
        </button>
      </div>
    </div>
  );
};
