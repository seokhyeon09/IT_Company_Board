import React from 'react';
import { Clock, AlertTriangle, CheckCircle2, UserCheck, HelpCircle } from 'lucide-react';
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

  if (isPast) {
    return (
      <span className="inline-flex items-center text-[10px] font-bold text-rose-700 bg-rose-50 border border-rose-200/80 px-2 py-0.5 rounded-full">
        <AlertTriangle className="w-3 h-3 mr-1 text-rose-500" />
        SLA {hours > 0 ? `${hours}시간 ` : ''}{minutes}분 초과
      </span>
    );
  }
  return (
    <span className="inline-flex items-center text-[10px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200/80 px-2 py-0.5 rounded-full">
      <Clock className="w-3 h-3 mr-1 text-emerald-500" />
      SLA {hours > 0 ? `${hours}시간 ` : ''}{minutes}분 남음
    </span>
  );
};

export const TicketCard: React.FC<TicketCardProps> = ({ ticket, onClick }) => {
  const currentStatus = statusMap[ticket.status] || {
    label: ticket.status,
    color: 'bg-slate-100 text-slate-700 border-slate-200',
  };
  const currentCategory = categoryMap[ticket.category] || ticket.category;
  const currentPriority = priorityMap[ticket.priority] || {
    label: '보통',
    badge: 'bg-slate-200 text-slate-700',
  };

  const slaBadge = formatSlaRemaining(ticket.deadline, ticket.is_overdue, ticket.status);

  return (
    <div
      onClick={() => onClick(ticket)}
      className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs hover:shadow-md transition-all duration-200 cursor-pointer flex flex-col justify-between group hover:border-indigo-300 relative overflow-hidden"
    >
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 group-hover:text-indigo-600 transition-colors">
            {ticket.ticket_number}
          </span>
          <div className="flex items-center space-x-1.5">
            {slaBadge}
            <span
              className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${currentStatus.color}`}
            >
              {currentStatus.label}
            </span>
          </div>
        </div>

        <div>
          <h3 className="font-bold text-slate-800 text-base group-hover:text-indigo-600 transition-colors line-clamp-1">
            {ticket.title}
          </h3>
        </div>
      </div>

      <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center space-x-2">
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${currentPriority.badge}`}>
            {currentPriority.label}
          </span>
          <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium text-[11px]">
            {currentCategory}
          </span>
        </div>

        <div className="flex items-center space-x-3 text-slate-400 text-[11px]">
          {ticket.assignee_name && (
            <span className="flex items-center text-slate-600 font-medium">
              <UserCheck className="w-3.5 h-3.5 mr-1 text-slate-400" />
              {ticket.assignee_name}
            </span>
          )}
          {ticket.deadline && (
            <span className="flex items-center">
              <Clock className="w-3.5 h-3.5 mr-1" />
              {new Date(ticket.deadline).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
