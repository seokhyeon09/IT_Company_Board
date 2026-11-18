import React from 'react';
import { Clock, AlertTriangle, HelpCircle, PauseCircle } from 'lucide-react';
import { statusMap, categoryMap, priorityMap } from '../../../shared/types/common';
import { Ticket } from '../types/ticket';
import { formatSlaRemaining } from '../../../shared/utils/slaUtils';

export type { Ticket };

interface TicketCardProps {
  ticket: Ticket;
  onClick: (ticket: Ticket) => void;
  selectable?: boolean;
  selected?: boolean;
  onToggleSelect?: (ticketId: number) => void;
}

export const TicketCard: React.FC<TicketCardProps> = ({
  ticket,
  onClick,
  selectable = false,
  selected = false,
  onToggleSelect,
}) => {
  const statusInfo = statusMap[ticket.status] || {
    label: ticket.status,
    color: 'bg-slate-100 text-slate-700',
  };
  const priorityInfo = priorityMap[ticket.priority] || {
    label: '보통',
    badge: 'bg-slate-200 text-slate-700',
  };

  const slaInfo = formatSlaRemaining(
    ticket.deadline,
    ticket.is_overdue,
    ticket.status,
    ticket.priority,
    ticket.sla_state
  );

  return (
    <div
      onClick={() => onClick(ticket)}
      className={`bg-white rounded-xl border p-5 shadow-xs hover:shadow-md hover:border-indigo-300 transition-all cursor-pointer flex flex-col justify-between ${
        selected ? 'border-indigo-500 ring-2 ring-indigo-200' : 'border-slate-200'
      }`}
    >
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            {selectable && (
              <input
                type="checkbox"
                aria-label="문의 선택"
                checked={selected}
                onClick={(e) => e.stopPropagation()}
                onChange={() => onToggleSelect?.(ticket.id)}
                className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
              />
            )}
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
            {ticket.merged_into_number && (
              <span className="text-[11px] bg-slate-100 text-slate-600 border border-slate-200 px-2 py-0.5 rounded font-medium">
                {ticket.merged_into_number} 에 병합됨
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
          <span>
            {ticket.create_date ? ticket.create_date.substring(0, 10) : ''}
          </span>
        </div>
      </div>

      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span className="truncate max-w-[140px]">
          담당: <strong className="text-slate-700 font-semibold">{ticket.assignee_name || '미배정'}</strong>
        </span>

        {slaInfo && (
          <span
            data-testid="ticket-sla-badge"
            className={`flex items-center px-2 py-0.5 rounded-full border text-[11px] ${slaInfo.badgeClass}`}
          >
            {slaInfo.isPaused ? (
              <PauseCircle className="w-3 h-3 mr-1 text-slate-500" />
            ) : slaInfo.isOverdue ? (
              <AlertTriangle className="w-3 h-3 mr-1 text-rose-600" />
            ) : slaInfo.isImminent ? (
              <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" />
            ) : (
              <Clock className="w-3 h-3 mr-1 text-slate-500" />
            )}
            {slaInfo.text}
          </span>
        )}
      </div>
    </div>
  );
};
