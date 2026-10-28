import React from 'react';
import {
  MessageSquare,
  Edit3,
  CheckSquare,
  PauseCircle,
  HelpCircle,
} from 'lucide-react';
import { ThreadItem } from '../../types/ticket';
import { formatHtmlContent } from '../../../../shared/utils/htmlUtils';

interface TicketTimelineProps {
  timeline: ThreadItem[] | undefined;
  isOfficer: boolean;
  isEditingResolution: boolean;
  onStartEditResolution: () => void;
}

export const TicketTimeline: React.FC<TicketTimelineProps> = ({
  timeline,
  isOfficer,
  isEditingResolution,
  onStartEditResolution,
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
            문의 및 조치 대화 타임라인 ({count}건)
          </h4>
        </div>
        {isOfficer && !isEditingResolution && hasResolution && (
          <button
            type="button"
            onClick={onStartEditResolution}
            className="flex items-center text-xs font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 px-2.5 py-1 rounded-lg transition-all cursor-pointer shadow-2xs"
          >
            <Edit3 className="w-3.5 h-3.5 mr-1" />
            답변 수정
          </button>
        )}
      </div>

      {/* Timeline Cards Container */}
      <div className="space-y-3">
        {timeline && timeline.length > 0 ? (
          timeline.map((item, idx) => {
            const isInquiry = item.type === 'inquiry';
            const isInitial = isInquiry && item.round === 1;
            const isPendingReq = item.type === 'pending_request';
            const isPendingResp = item.type === 'pending_response';

            let cardStyle = 'bg-emerald-50/50 border-emerald-200 text-slate-800';
            let titleText = `답변 ${item.round}차`;
            let icon = <CheckSquare className="w-4 h-4 text-emerald-600" />;
            let badgeBg = 'bg-emerald-100 text-emerald-800 border-emerald-200';

            if (isPendingReq) {
              cardStyle = 'bg-purple-50/60 border-purple-200 text-purple-950';
              titleText = '답변 대기 요청';
              icon = <PauseCircle className="w-4 h-4 text-purple-600" />;
              badgeBg = 'bg-purple-100 text-purple-800 border-purple-200';
            } else if (isPendingResp) {
              cardStyle = 'bg-blue-50/60 border-blue-200 text-blue-950';
              titleText = '답변 대기 회신';
              icon = <MessageSquare className="w-4 h-4 text-blue-600" />;
              badgeBg = 'bg-blue-100 text-blue-800 border-blue-200';
            } else if (isInitial) {
              cardStyle = 'bg-slate-50 border-slate-200 text-slate-800';
              titleText = '최초 문의';
              icon = <MessageSquare className="w-4 h-4 text-slate-500" />;
              badgeBg = 'bg-slate-100 text-slate-700 border-slate-200';
            } else if (isInquiry) {
              cardStyle = 'bg-indigo-50/60 border-indigo-200 text-indigo-950';
              titleText = `재문의 ${item.round}차`;
              icon = <HelpCircle className="w-4 h-4 text-indigo-600" />;
              badgeBg = 'bg-indigo-100 text-indigo-800 border-indigo-200';
            }

            return (
              <div
                key={item.id || idx}
                className={`p-4 rounded-xl border space-y-2 shadow-2xs transition-all ${cardStyle}`}
              >
                <div className="flex items-center justify-between text-xs pb-1.5 border-b border-black/5">
                  <div className="flex items-center space-x-2">
                    {icon}
                    <span className={`font-bold px-2 py-0.5 rounded-md text-[11px] border ${badgeBg}`}>
                      {titleText}
                    </span>
                    <span className="font-semibold text-slate-700">
                      {item.author_name}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-400">
                    {item.date ? new Date(item.date).toLocaleString() : ''}
                  </span>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-wrap pl-1">
                  {formatHtmlContent(item.content)}
                </p>
              </div>
            );
          })
        ) : (
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-500 italic">
            타임라인 이력이 없습니다.
          </div>
        )}
      </div>
    </div>
  );
};
