import React from 'react';
import { Clock, AlertTriangle, HelpCircle } from 'lucide-react';
import { statusMap, categoryMap, priorityMap } from '../../../shared/types/common';

export interface Ticket {
  id: number;
  ticket_number: string;
  title: string;
  category: string;
  status: string;
  priority: string;
  deadline?: string;
  is_overdue: boolean;
  author_id?: any;
  assignee_id?: any;
  assignee_name?: string;
  create_date?: string;
  write_date?: string;
  is_faq: boolean;
}

interface TicketCardProps {
  ticket: Ticket;
  onClick: (ticket: Ticket) => void;
}

const formatSlaRemaining = (deadlineStr?: string, isOverdue?: boolean, status?: string) => {
  if (!deadlineStr || ['resolved', 'closed', 'canceled'].includes(status || '')) return null;
  const deadline = new Date(deadlineStr).getTime();
  const now = Date.now();
  const diffMs = deadline - now;
  const isPast = diffMs < 0 || isOverdue;

  const absMinutes = Math.floor(Math.abs(diffMs) / (1000 * 60));
  const hours = Math.floor(absMinutes / 60);
  const minutes = absMinutes % 60;
  const days = Math.floor(hours / 24);

  let timeText = '';
  if (days > 0) {
    timeText = `${days}일 ${hours % 24}시간`;
  } else if (hours > 0) {
    timeText = `${hours}시간 ${minutes}분`;
  } else {
    timeText = `${minutes}분`;
  }

  if (isPast) {
    return {
      text: `SLA ${timeText} 초과`,
      badgeClass: 'bg-rose-50 text-rose-700 border-rose-200 font-bold',
      isOverdue: true,
    };
  } else {
    return {
      text: `SLA ${timeText} 남음`,
      badgeClass: hours < 4 ? 'bg-amber-50 text-amber-700 border-amber-200 font-semibold' : 'bg-slate-50 text-slate-600 border-slate-200',
      isOverdue: false,
    };
  }
};

export const TicketCard: React.FC<TicketCardProps> = ({ ticket, onClick }) => {
  const statusInfo = statusMap[ticket.status] || { label: ticket.status, color: 'bg-slate-100 text-slate-700' };
  const priorityInfo = priorityMap[ticket.priority] || { label: '보통', badge: 'bg-slate-200 text-slate-700' };

  return (
    <div
      onClick={() => onClick(ticket)}
      className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md hover:border-indigo-300 transition-all cursor-pointer flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              {ticket.ticket_number}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded font-semibold ${priorityInfo.badge}`}>
              {priorityInfo.label}
            </span>
            {ticket.is_faq && (
              <span className="flex items-center text-xs bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded font-medium">
                <HelpCircle className="w-3 h-3 mr-1" /> FAQ
              </span>
            )}
          </div>
          <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${statusInfo.color}`}>
            {statusInfo.label}
          </span>
        </div>

        <h3 className="font-bold text-base text-slate-900 group-hover:text-indigo-600 line-clamp-1 mb-2">
          {ticket.title}
        </h3>

        <div className="flex items-center space-x-2 text-xs text-slate-500 mb-4">
          <span className="bg-slate-100 px-2 py-0.5 rounded text-slate-600 font-medium">
            {categoryMap[ticket.category] || ticket.category}
          </span>
          <span>·</span>
          <span>담당자: {ticket.assignee_name || '배정 대기'}</span>
        </div>
      </div>

      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
        <div className="text-slate-400">
          접수: {ticket.create_date ? ticket.create_date.substring(0, 10) : '-'}
        </div>

        {ticket.deadline && (() => {
          const slaInfo = formatSlaRemaining(ticket.deadline, ticket.is_overdue, ticket.status);
          return (
            <div className="flex items-center text-xs">
              {slaInfo ? (
                <span className={`flex items-center px-2 py-0.5 rounded border text-[11px] ${slaInfo.badgeClass}`}>
                  {slaInfo.isOverdue ? (
                    <AlertTriangle className="w-3 h-3 mr-1 text-rose-500" />
                  ) : (
                    <Clock className="w-3 h-3 mr-1 text-amber-500" />
                  )}
                  {slaInfo.text}
                </span>
              ) : (
                <span className="flex items-center text-slate-400 text-[11px]">
                  <Clock className="w-3 h-3 mr-1" />
                  {ticket.deadline.substring(5, 16).replace('T', ' ')}
                </span>
              )}
            </div>
          );
        })()}
      </div>
    </div>
  );
};
