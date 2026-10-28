import React from 'react';

interface InquiryEditFormProps {
  editTitle: string;
  setEditTitle: (val: string) => void;
  editCategory: string;
  setEditCategory: (val: string) => void;
  editPriority: string;
  setEditPriority: (val: string) => void;
  editContent: string;
  setEditContent: (val: string) => void;
  submitting: boolean;
  error?: string | null;
  onCancel: () => void;
  onSubmit: (e: React.FormEvent) => void;
}

export const InquiryEditForm: React.FC<InquiryEditFormProps> = ({
  editTitle,
  setEditTitle,
  editCategory,
  setEditCategory,
  editPriority,
  setEditPriority,
  editContent,
  setEditContent,
  submitting,
  error,
  onCancel,
  onSubmit,
}) => {
  return (
    <div className="mt-3 p-4 bg-indigo-50/70 border border-indigo-200 rounded-xl space-y-3 animate-in fade-in">
      <div className="text-xs font-bold text-indigo-900">접수 대기 중 문의 내용 수정</div>
      <form onSubmit={onSubmit} className="space-y-3">
        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">문의 제목</label>
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="w-full px-3 py-1.5 text-xs border border-indigo-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-800"
            required
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">카테고리</label>
            <select
              value={editCategory}
              onChange={(e) => setEditCategory(e.target.value)}
              className="w-full px-2.5 py-1.5 text-xs border border-indigo-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-800"
            >
              <option value="hw">하드웨어</option>
              <option value="sw">소프트웨어</option>
              <option value="network">네트워크</option>
              <option value="account">계정/권한</option>
              <option value="etc">기타</option>
            </select>
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">긴급도 (우선순위)</label>
            <select
              value={editPriority}
              onChange={(e) => setEditPriority(e.target.value)}
              className="w-full px-2.5 py-1.5 text-xs border border-indigo-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-800"
            >
              <option value="0">낮음</option>
              <option value="1">보통</option>
              <option value="2">높음</option>
              <option value="3">긴급</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">상세 내용</label>
          <textarea
            rows={3}
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className="w-full px-3 py-2 text-xs border border-indigo-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-800 resize-none"
            required
          />
        </div>
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
            className="px-3.5 py-1.5 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 cursor-pointer"
          >
            {submitting ? '수정 저장 중...' : '수정 완료'}
          </button>
        </div>
      </form>
    </div>
  );
};
