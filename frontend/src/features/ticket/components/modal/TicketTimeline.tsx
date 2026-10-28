import React from 'react';
import {
  MessageSquare,
  Edit3,
  CheckCircle2,
  PauseCircle,
  Loader2,
} from 'lucide-react';
import { ThreadItem } from '../../types/ticket';
import { formatHtmlContent } from '../../../../shared/utils/htmlUtils';

interface TicketTimelineProps {
  timeline: ThreadItem[] | undefined;
  fallbackContent?: string;
  isOfficer: boolean;
  isEditingResolution: boolean;
  onStartEditResolution: () => void;
  editResolutionNote: string;
  setEditResolutionNote: (val: string) => void;
  submittingEditResolution: boolean;
  editResolutionError: string;
  onCancelEditResolution: () => void;
  onSubmitEditResolution: (e: React.FormEvent) => void;
}

export const TicketTimeline: React.FC<TicketTimelineProps> = ({
  timeline,
  fallbackContent,
  isOfficer,
  isEditingResolution,
  onStartEditResolution,
  editResolutionNote,
  setEditResolutionNote,
  submittingEditResolution,
  editResolutionError,
  onCancelEditResolution,
  onSubmitEditResolution,
}) => {
  const count = timeline && timeline.length > 0 ? timeline.length : 1;
  const hasResolution = timeline && timeline.some((t) => t.type === 'resolution');

  return (
    <div className="space-y-3">
      {/* Timeline Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-1.5">
          <MessageSquare className="w-4 h-4 text-indigo-600" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
            문의 및 조치 대화 진행 타임라인 ({count}건)
          </h4>
        </div>
        {isOfficer && !isEditingResolution && hasResolution && (
          <button
            type="button"
            onClick={onStartEditResolution}
            className="flex items-center text-xs font-semibold text-emerald-700 hover:text-emerald-900 bg-white border border-emerald-300 hover:bg-emerald-100/50 px-2.5 py-1 rounded-lg transition-all cursor-pointer shadow-xs"
          >
            <Edit3 className="w-3.5 h-3.5 mr-1" />
            최신 답변 수정
          </button>
        )}
      </div>

      {/* Edit Form for latest resolution (Inline right below timeline header) */}
      {isEditingResolution && (
        <div className="p-4 bg-emerald-50/90 border border-emerald-300 rounded-xl shadow-xs animate-in fade-in">
          <div className="text-xs font-bold text-emerald-900 mb-2">최신 조치 내용 수정</div>
          <form onSubmit={onSubmitEditResolution} className="space-y-3">
            <textarea
              rows={3}
              value={editResolutionNote}
              onChange={(e) => setEditResolutionNote(e.target.value)}
              className="w-full px-3.5 py-2.5 text-xs border border-emerald-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none text-slate-800"
              placeholder="수정할 조치 내용을 입력하세요 (최소 5자)..."
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
                className="flex items-center px-3.5 py-1.5 text-xs font-semibold text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-all cursor-pointer"
              >
                {submittingEditResolution ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                    저장 중...
                  </>
                ) : (
                  '수정 저장'
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Timeline Cards Container */}
      <div className="space-y-3">
        {timeline && timeline.length > 0 ? (
          timeline.map((item, idx) => {
            const isInquiry = item.type === 'inquiry';
            const isInitial = isInquiry && item.round === 1;
            const isPendingReq = item.type === 'pending_request';
            const isPendingResp = item.type === 'pending_response';

            return (
              <div
                key={item.id || idx}
                className={`p-4 rounded-xl border space-y-2 shadow-xs transition-all ${
                  isInitial
                    ? 'bg-slate-50 border-slate-200 text-slate-800'
                    : isPendingReq
                    ? 'bg-amber-50/90 border-amber-200 text-amber-950'
                    : isPendingResp
                    ? 'bg-blue-50/90 border-blue-200 text-blue-950'
                    : isInquiry
                    ? 'bg-purple-50/90 border-purple-200 text-purple-950'
                    : 'bg-emerald-50/80 border-emerald-200 text-emerald-950'
                }`}
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold flex items-center">
                    {isPendingReq ? (
                      <span className="bg-amber-200 text-amber-900 text-[10px] px-2 py-0.5 rounded-full mr-2 font-mono font-semibold flex items-center border border-amber-300">
                        <PauseCircle className="w-3 h-3 mr-1 text-amber-700" />
                        IT 담당자 답변 대기 요청
                      </span>
                    ) : isPendingResp ? (
                      <span className="bg-blue-200 text-blue-900 text-[10px] px-2 py-0.5 rounded-full mr-2 font-mono font-semibold flex items-center border border-blue-300">
                        <MessageSquare className="w-3 h-3 mr-1 text-blue-700" />
                        답변 대기 회신
                      </span>
                    ) : isInquiry ? (
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full mr-2 font-mono font-semibold flex items-center ${
                          isInitial ? 'bg-slate-200 text-slate-700' : 'bg-purple-200 text-purple-800'
                        }`}
                      >
                        <MessageSquare className="w-3 h-3 mr-1" />
                        문의 {item.round}차
                      </span>
                    ) : (
                      <span className="bg-emerald-200 text-emerald-800 text-[10px] px-2 py-0.5 rounded-full mr-2 font-mono font-semibold flex items-center">
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        답변 {item.round}차
                      </span>
                    )}
                    <span
                      className={
                        isPendingReq
                          ? 'text-amber-950'
                          : isPendingResp
                          ? 'text-blue-950'
                          : isInquiry
                          ? isInitial
                            ? 'text-slate-800'
                            : 'text-purple-900'
                          : 'text-emerald-900'
                      }
                    >
                      {item.author_name}
                    </span>
                  </span>
                  <span className="text-[11px] text-slate-400 font-mono">
                    {item.date ? item.date.substring(0, 16).replace('T', ' ') : '-'}
                  </span>
                </div>

                <div className="text-sm whitespace-pre-wrap leading-relaxed">
                  {formatHtmlContent(item.content)}
                </div>
              </div>
            );
          })
        ) : (
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 whitespace-pre-wrap leading-relaxed text-sm">
            {formatHtmlContent(fallbackContent) || '작성된 상세 내용이 없습니다.'}
          </div>
        )}
      </div>
    </div>
  );
};
