import React from 'react';
import { History, Edit3 } from 'lucide-react';
import { TicketLog } from '../../types/ticket';
import { formatHtmlContent } from '../../../../shared/utils/htmlUtils';

interface TicketOfficerLogsProps {
  logs: TicketLog[] | undefined;
  isOfficer: boolean;
}

export const TicketOfficerLogs: React.FC<TicketOfficerLogsProps> = ({
  logs,
  isOfficer,
}) => {
  if (!isOfficer || !logs || logs.length === 0) {
    return null;
  }

  return (
    <div className="pt-4 border-t border-slate-200">
      <div className="flex items-center space-x-1.5 mb-3">
        <History className="w-4 h-4 text-slate-500" />
        <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
          IT 담당자 활동 및 처리 이력 ({logs.length}건)
        </h4>
        <span className="text-[10px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded border border-slate-200">
          사원 비노출
        </span>
      </div>
      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
        {logs.map((log) => (
          <div
            key={log.id}
            className="p-3 bg-slate-50 border border-slate-200/80 rounded-xl text-xs space-y-1"
          >
            <div className="flex items-center justify-between text-slate-500 text-[11px]">
              <span className="font-semibold text-slate-700">{log.author_name}</span>
              <span>{log.date ? log.date.substring(0, 16).replace('T', ' ') : '-'}</span>
            </div>
            {log.body.includes('[답변 내용 수정 이력]') ? (
              <div className="space-y-1.5 mt-1 bg-amber-50/70 p-2.5 rounded-lg border border-amber-200 text-xs">
                <div className="font-bold text-amber-900 flex items-center text-[11px]">
                  <Edit3 className="w-3 h-3 mr-1 text-amber-700" />
                  답변 내용 수정 내역
                </div>
                <div className="text-[11px] text-slate-500 line-through bg-white/70 p-1.5 rounded border border-slate-200">
                  <span className="font-semibold text-slate-600 mr-1">[수정 전]</span>
                  {formatHtmlContent(log.body.split('[수정 전]')[1]?.split('[수정 후]')[0])}
                </div>
                <div className="text-[11px] font-semibold text-emerald-800 bg-emerald-50 p-1.5 rounded border border-emerald-200">
                  <span className="font-bold text-emerald-700 mr-1">[수정 후]</span>
                  {formatHtmlContent(log.body.split('[수정 후]')[1])}
                </div>
              </div>
            ) : (
              <p className="text-slate-800 whitespace-pre-wrap leading-relaxed">
                {formatHtmlContent(log.body)}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
