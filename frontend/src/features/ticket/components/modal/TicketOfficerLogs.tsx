import React from 'react';
import { History } from 'lucide-react';
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
    <div className="pt-3 border-t border-slate-200/80 space-y-2">
      <div className="flex items-center space-x-1.5">
        <History className="w-4 h-4 text-slate-500" />
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">
          시스템 감사 및 처리 로그 ({logs.length}건, 담당자 전용)
        </h4>
      </div>
      <div className="max-h-48 overflow-y-auto space-y-2 p-2.5 bg-slate-100/70 rounded-xl border border-slate-200">
        {logs.map((log) => (
          <div
            key={log.id}
            className="text-xs text-slate-600 border-b border-slate-200/50 pb-1.5 last:border-b-0 space-y-0.5"
          >
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span className="font-semibold text-slate-700">{log.author_name}</span>
              <span>{log.date ? new Date(log.date).toLocaleString() : ''}</span>
            </div>
            <p className="whitespace-pre-wrap leading-relaxed text-slate-600 pl-0.5">
              {formatHtmlContent(log.body)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
