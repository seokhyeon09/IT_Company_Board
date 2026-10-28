import React from 'react';
import { RotateCcw, Loader2 } from 'lucide-react';

interface RestartInquiryFormProps {
  isAuthor: boolean;
  isResolved: boolean;
  isClosed: boolean;
  showRestartForm: boolean;
  onOpenRestart: () => void;
  onCloseRestart: () => void;
  restartReason: string;
  setRestartReason: (val: string) => void;
  submittingRestart: boolean;
  restartError: string;
  onSubmitRestart: (e: React.FormEvent) => void;
}

export const RestartInquiryForm: React.FC<RestartInquiryFormProps> = ({
  isAuthor,
  isResolved,
  isClosed,
  showRestartForm,
  onOpenRestart,
  onCloseRestart,
  restartReason,
  setRestartReason,
  submittingRestart,
  restartError,
  onSubmitRestart,
}) => {
  return (
    <>
      {isAuthor && isResolved && (
        <div className="p-4 bg-purple-50/70 border border-purple-200 rounded-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1.5">
              <RotateCcw className="w-4 h-4 text-purple-600" />
              <span className="text-xs font-bold text-purple-900 uppercase tracking-wider">
                추가 재문의가 필요하신가요?
              </span>
            </div>
            {!showRestartForm && (
              <button
                type="button"
                onClick={onOpenRestart}
                className="flex items-center text-xs font-semibold text-purple-700 bg-white border border-purple-300 hover:bg-purple-100/70 px-2.5 py-1 rounded-lg transition-all cursor-pointer shadow-2xs"
              >
                추가 재문의 작성
              </button>
            )}
          </div>

          {showRestartForm && (
            <form onSubmit={onSubmitRestart} className="space-y-3 mt-3">
              <p className="text-xs text-purple-800">
                조치 내용에 미흡한 점이 있거나 추가 문의사항이 있으시면 입력해 주세요. 담당자에게 알림이 전달되며 처리가 다시 시작됩니다.
              </p>
              <textarea
                value={restartReason}
                onChange={(e) => setRestartReason(e.target.value)}
                placeholder="재문의할 내용을 구체적으로 작성해 주세요..."
                rows={3}
                required
                className="w-full text-xs p-2.5 bg-white border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 resize-none"
              />
              {restartError && (
                <p className="text-xs text-rose-600 font-medium">{restartError}</p>
              )}
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={onCloseRestart}
                  className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
                >
                  취소
                </button>
                <button
                  type="submit"
                  disabled={submittingRestart}
                  className="flex items-center px-3.5 py-1.5 text-xs font-semibold text-white bg-purple-600 hover:bg-purple-700 rounded-lg shadow-2xs cursor-pointer"
                >
                  {submittingRestart && <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />}
                  재문의 등록
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {isClosed && (
        <div className="p-3 bg-slate-100 border border-slate-200 rounded-xl text-center text-xs text-slate-500 font-medium">
          본 문의는 최종 종결 처리되어 추가 재문의가 불가합니다.
        </div>
      )}
    </>
  );
};
