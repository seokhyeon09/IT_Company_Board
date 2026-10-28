import React from 'react';
import { PauseCircle, Loader2 } from 'lucide-react';

interface PendingRequestFormProps {
  pendingReason: string;
  setPendingReason: (val: string) => void;
  submitting: boolean;
  error?: string | null;
  onCancel: () => void;
  onSubmit: (e: React.FormEvent) => void;
}

export const PendingRequestForm: React.FC<PendingRequestFormProps> = ({
  pendingReason,
  setPendingReason,
  submitting,
  error,
  onCancel,
  onSubmit,
}) => {
  return (
    <div className="p-3 bg-white border border-purple-200 rounded-lg space-y-2 animate-in fade-in">
      <div className="text-xs font-bold text-slate-800 flex items-center justify-between">
        <span className="flex items-center text-purple-900">
          <PauseCircle className="w-3.5 h-3.5 mr-1 text-purple-600" />
          답변 대기 상태로 전환 (사원 추가 확인 요청)
        </span>
        <button
          type="button"
          onClick={onCancel}
          className="text-slate-400 hover:text-slate-600 text-xs cursor-pointer"
        >
          닫기
        </button>
      </div>
      <p className="text-[11px] text-slate-500 leading-snug">
        사원에게 추가 확인이 필요한 내용을 구체적으로 입력하세요. 대기 사유가 사원 화면과 타임라인에 안내됩니다.
      </p>
      <form onSubmit={onSubmit} className="space-y-2">
        <textarea
          rows={2}
          value={pendingReason}
          onChange={(e) => setPendingReason(e.target.value)}
          placeholder="예: 발생한 오류 캡처 화면 또는 상세 에러 로그 첨부 부탁드립니다."
          className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-purple-500 text-slate-800 resize-none"
          required
        />
        {error && <p className="text-xs text-rose-600 font-medium">{error}</p>}
        <div className="flex justify-end space-x-2">
          <button
            type="button"
            onClick={onCancel}
            className="px-2.5 py-1 text-xs text-slate-600 bg-white border border-slate-200 rounded-md hover:bg-slate-50 cursor-pointer"
          >
            취소
          </button>
          <button
            type="submit"
            disabled={submitting || !pendingReason.trim()}
            className="flex items-center px-3 py-1 text-xs font-semibold text-white bg-purple-600 rounded-md hover:bg-purple-700 disabled:opacity-50 cursor-pointer shadow-xs"
          >
            {submitting ? (
              <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
            ) : (
              <PauseCircle className="w-3.5 h-3.5 mr-1" />
            )}
            대기 상태 전환 확정
          </button>
        </div>
      </form>
    </div>
  );
};
