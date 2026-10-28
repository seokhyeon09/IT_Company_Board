import React from 'react';
import { Lock, Loader2 } from 'lucide-react';

interface ForceCloseFormProps {
  closeNote: string;
  setCloseNote: (val: string) => void;
  submitting: boolean;
  error?: string | null;
  onCancel: () => void;
  onSubmit: (e: React.FormEvent) => void;
}

export const ForceCloseForm: React.FC<ForceCloseFormProps> = ({
  closeNote,
  setCloseNote,
  submitting,
  error,
  onCancel,
  onSubmit,
}) => {
  return (
    <div className="p-3 bg-white border border-slate-300 rounded-lg space-y-2 animate-in fade-in">
      <div className="text-xs font-bold text-slate-800 flex items-center justify-between">
        <span className="flex items-center text-slate-800">
          <Lock className="w-3.5 h-3.5 mr-1 text-slate-600" />
          티켓 직권 종결
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
        문의자 부재, 중복 접수, 기타 사유로 추가 조치 없이 티켓을 즉시 종결합니다. 종결 사유를 입력하세요.
      </p>
      <form onSubmit={onSubmit} className="space-y-2">
        <textarea
          rows={2}
          value={closeNote}
          onChange={(e) => setCloseNote(e.target.value)}
          placeholder="종결 사유 입력 (선택)..."
          className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-slate-500 text-slate-800 resize-none"
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
            disabled={submitting}
            className="flex items-center px-3 py-1 text-xs font-semibold text-white bg-slate-700 rounded-md hover:bg-slate-800 disabled:opacity-50 cursor-pointer shadow-xs"
          >
            {submitting ? (
              <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
            ) : (
              <Lock className="w-3.5 h-3.5 mr-1" />
            )}
            종결 확정
          </button>
        </div>
      </form>
    </div>
  );
};
