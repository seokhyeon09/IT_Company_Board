import React from 'react';

interface PendingReplyFormProps {
  pendingReplyText: string;
  setPendingReplyText: (val: string) => void;
  submitting: boolean;
  error?: string | null;
  onCancel: () => void;
  onSubmit: (e: React.FormEvent) => void;
}

export const PendingReplyForm: React.FC<PendingReplyFormProps> = ({
  pendingReplyText,
  setPendingReplyText,
  submitting,
  error,
  onCancel,
  onSubmit,
}) => {
  return (
    <form onSubmit={onSubmit} className="space-y-2.5 animate-in fade-in">
      <div className="text-xs font-bold text-purple-900">
        답변 대기 요청에 대한 추가 정보/답변 입력
      </div>
      <textarea
        rows={3}
        value={pendingReplyText}
        onChange={(e) => setPendingReplyText(e.target.value)}
        placeholder="IT 담당자가 요청한 추가 정보나 확인 사항에 대해 답변을 입력하세요 (최소 5자)..."
        className="w-full px-3.5 py-2 text-xs border border-purple-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none text-slate-800"
      />
      {error && <p className="text-xs text-rose-600 font-medium">{error}</p>}
      <div className="flex justify-end space-x-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
        >
          취소
        </button>
        <button
          type="submit"
          disabled={submitting}
          className="flex items-center px-3.5 py-1.5 text-xs font-semibold text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-all cursor-pointer shadow-xs"
        >
          {submitting ? '등록 중...' : '답변 회신 등록'}
        </button>
      </div>
    </form>
  );
};
