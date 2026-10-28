import React from 'react';
import { CheckCircle2, Loader2 } from 'lucide-react';

interface ResolutionFormProps {
  canResolve: boolean;
  isEditingResolution: boolean;
  editResolutionNote: string;
  setEditResolutionNote: (val: string) => void;
  submittingEditResolution: boolean;
  editResolutionError: string;
  onCancelEditResolution: () => void;
  onSubmitEditResolution: (e: React.FormEvent) => void;
  resolutionNote: string;
  setResolutionNote: (val: string) => void;
  submittingResolve: boolean;
  resolveError: string;
  onSubmitResolve: (e: React.FormEvent) => void;
}

export const ResolutionForm: React.FC<ResolutionFormProps> = ({
  canResolve,
  isEditingResolution,
  editResolutionNote,
  setEditResolutionNote,
  submittingEditResolution,
  editResolutionError,
  onCancelEditResolution,
  onSubmitEditResolution,
  resolutionNote,
  setResolutionNote,
  submittingResolve,
  resolveError,
  onSubmitResolve,
}) => {
  if (isEditingResolution) {
    return (
      <div className="p-4 bg-emerald-50/90 border border-emerald-300 rounded-xl shadow-2xs">
        <div className="text-xs font-bold text-emerald-900 mb-2">최신 조치 내용 수정</div>
        <form onSubmit={onSubmitEditResolution} className="space-y-3">
          <textarea
            value={editResolutionNote}
            onChange={(e) => setEditResolutionNote(e.target.value)}
            placeholder="수정할 조치 내용을 구체적으로 입력해 주세요 (최소 5자 이상)..."
            rows={4}
            required
            className="w-full text-xs p-3 bg-white border border-emerald-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none leading-relaxed"
          />
          {editResolutionError && (
            <p className="text-xs text-rose-600 font-medium">{editResolutionError}</p>
          )}
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onCancelEditResolution}
              className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={submittingEditResolution}
              className="flex items-center px-3.5 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-2xs cursor-pointer"
            >
              {submittingEditResolution && <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />}
              수정 저장
            </button>
          </div>
        </form>
      </div>
    );
  }

  if (canResolve) {
    return (
      <div className="p-4 bg-emerald-50/60 border border-emerald-200 rounded-xl space-y-3">
        <div className="flex items-center space-x-1.5">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-900">
            IT 담당자 조치 답변 작성
          </h4>
        </div>
        <form onSubmit={onSubmitResolve} className="space-y-3">
          <textarea
            value={resolutionNote}
            onChange={(e) => setResolutionNote(e.target.value)}
            placeholder="요청 사항에 대한 해결 조치 결과 및 안내 사항을 자세히 작성해 주세요..."
            rows={4}
            required
            className="w-full text-xs p-3 bg-white border border-emerald-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none leading-relaxed"
          />
          {resolveError && (
            <p className="text-xs text-rose-600 font-medium">{resolveError}</p>
          )}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={submittingResolve}
              className="flex items-center px-4 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-2xs cursor-pointer transition-colors"
            >
              {submittingResolve && <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />}
              조치 완료 처리
            </button>
          </div>
        </form>
      </div>
    );
  }

  return null;
};
