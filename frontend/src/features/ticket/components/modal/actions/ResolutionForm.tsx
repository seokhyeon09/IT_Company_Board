import React from 'react';
import { ShieldCheck, CheckCircle2, Loader2 } from 'lucide-react';

interface ResolutionFormProps {
  canResolve: boolean;
  resolutionNote: string;
  setResolutionNote: (val: string) => void;
  submittingResolve: boolean;
  resolveError: string;
  onSubmitResolve: (e: React.FormEvent) => void;
}

export const ResolutionForm: React.FC<ResolutionFormProps> = ({
  canResolve,
  resolutionNote,
  setResolutionNote,
  submittingResolve,
  resolveError,
  onSubmitResolve,
}) => {
  if (!canResolve) {
    return null;
  }

  return (
    <div className="pt-4 border-t border-slate-200">
      <div className="flex items-center space-x-1.5 mb-2">
        <ShieldCheck className="w-4 h-4 text-indigo-600" />
        <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
          IT 담당자 해결 조치 등록
        </h4>
      </div>

      <form onSubmit={onSubmitResolve} className="space-y-3">
        <textarea
          rows={3}
          value={resolutionNote}
          onChange={(e) => setResolutionNote(e.target.value)}
          placeholder="처리 완료된 구체적인 조치 내용(예: 부품 교체 완료, 원격 세팅 지원 등)을 최소 5자 이상 입력하세요..."
          className="w-full px-3.5 py-2.5 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
        />

        {resolveError && (
          <div className="text-xs text-rose-600 bg-rose-50 border border-rose-200 p-2.5 rounded-lg">
            {resolveError}
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={submittingResolve}
            className="flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-md shadow-emerald-600/20 disabled:opacity-50 transition-all cursor-pointer"
          >
            {submittingResolve ? (
              <>
                <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                처리 중...
              </>
            ) : (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                해결 완료 처리
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
