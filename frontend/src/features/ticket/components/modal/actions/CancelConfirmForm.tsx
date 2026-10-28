import React from 'react';
import { Ban } from 'lucide-react';

interface CancelConfirmFormProps {
  cancelReason: string;
  setCancelReason: (val: string) => void;
  submitting: boolean;
  error?: string | null;
  onCancel: () => void;
  onSubmit: (e: React.FormEvent) => void;
}

export const CancelConfirmForm: React.FC<CancelConfirmFormProps> = ({
  cancelReason,
  setCancelReason,
  submitting,
  error,
  onCancel,
  onSubmit,
}) => {
  return (
    <div className="mt-3 p-4 bg-rose-50/90 border border-rose-300 rounded-xl space-y-2.5 animate-in fade-in shadow-xs">
      <div className="flex items-center justify-between">
        <div className="text-xs font-bold text-rose-900 flex items-center">
          <Ban className="w-4 h-4 mr-1.5 text-rose-600" />
          문의 취소 확인
        </div>
      </div>
      <p className="text-xs text-rose-700 leading-relaxed">
        문의를 취소하면 IT 지원 처리가 즉시 중단되며 티켓이 취소 상태로 변경됩니다. 취소 사유를 입력해주세요.
      </p>
      <form onSubmit={onSubmit} className="space-y-2.5">
        <input
          type="text"
          value={cancelReason}
          onChange={(e) => setCancelReason(e.target.value)}
          placeholder="취소 사유를 입력하세요 (선택)..."
          className="w-full px-3 py-2 text-xs border border-rose-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-rose-500 text-slate-800"
        />
        {error && <p className="text-xs text-rose-600 font-medium">{error}</p>}
        <div className="flex justify-end space-x-2">
          <button
            type="button"
            onClick={onCancel}
            className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
          >
            취소 철회
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="flex items-center px-3.5 py-1.5 text-xs font-semibold text-white bg-rose-600 rounded-lg hover:bg-rose-700 disabled:opacity-50 cursor-pointer shadow-xs"
          >
            {submitting ? '취소 처리 중...' : '문의 취소 확정'}
          </button>
        </div>
      </form>
    </div>
  );
};
