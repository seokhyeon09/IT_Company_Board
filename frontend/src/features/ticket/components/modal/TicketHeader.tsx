import React from 'react';
import {
  X,
  Tag,
  ShieldCheck,
  BookmarkPlus,
  BookmarkCheck,
  Edit3,
  Ban,
  Loader2,
} from 'lucide-react';
import { TicketDetail } from '../../types/ticket';
import { statusMap, categoryMap, priorityMap } from '../../../../shared/types/common';

interface TicketHeaderProps {
  ticket: TicketDetail;
  isOfficer: boolean;
  isAuthor: boolean;
  togglingFaq: boolean;
  onToggleFaq: () => void;
  onClose: () => void;
  onOpenCancel: () => void;
  isEditingTicket: boolean;
  onStartEditTicket: () => void;
}

export const TicketHeader: React.FC<TicketHeaderProps> = ({
  ticket,
  isOfficer,
  isAuthor,
  togglingFaq,
  onToggleFaq,
  onClose,
  onOpenCancel,
  isEditingTicket,
  onStartEditTicket,
}) => {
  const currentStatus = statusMap[ticket.status] || {
    label: ticket.status,
    color: 'bg-slate-100 text-slate-700 border-slate-200',
  };
  const currentCategory = categoryMap[ticket.category] || ticket.category;
  const currentPriority = priorityMap[ticket.priority] || {
    label: '보통',
    badge: 'bg-slate-200 text-slate-700',
  };

  const canCancel =
    !['closed', 'canceled'].includes(ticket.status) && (isAuthor || isOfficer);
  const canEdit = isAuthor && ticket.status === 'submitted' && !isEditingTicket;

  return (
    <div className="flex items-center justify-between p-6 border-b border-slate-100 bg-slate-50/50">
      <div className="flex items-center space-x-3">
        <span className="text-xs font-bold text-slate-500 bg-white px-2.5 py-1 rounded-md border border-slate-200 shadow-2xs flex items-center">
          <Tag className="w-3.5 h-3.5 mr-1 text-slate-400" />
          {ticket.ticket_number}
        </span>
        <span
          className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${currentStatus.color}`}
        >
          {currentStatus.label}
        </span>
        <span
          className={`text-xs font-bold px-2 py-0.5 rounded-full ${currentPriority.badge}`}
        >
          {currentPriority.label}
        </span>
        <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
          {currentCategory}
        </span>
      </div>

      <div className="flex items-center space-x-2">
        {canEdit && (
          <button
            type="button"
            onClick={onStartEditTicket}
            className="flex items-center text-xs font-semibold text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1 rounded-lg border border-indigo-200 cursor-pointer transition-colors"
          >
            <Edit3 className="w-3.5 h-3.5 mr-1" />
            문의 수정
          </button>
        )}

        {canCancel && (
          <button
            type="button"
            onClick={onOpenCancel}
            className="flex items-center text-xs font-semibold text-rose-600 hover:text-rose-800 bg-rose-50 hover:bg-rose-100 px-2.5 py-1 rounded-lg border border-rose-200 cursor-pointer transition-colors"
          >
            <Ban className="w-3.5 h-3.5 mr-1" />
            문의 취소
          </button>
        )}

        {isOfficer && (
          <button
            type="button"
            onClick={onToggleFaq}
            disabled={togglingFaq}
            className={`flex items-center text-xs font-medium px-2.5 py-1 rounded-lg border transition-all cursor-pointer ${
              ticket.is_faq
                ? 'bg-amber-50 text-amber-800 border-amber-300 hover:bg-amber-100'
                : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
            }`}
          >
            {togglingFaq ? (
              <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
            ) : ticket.is_faq ? (
              <BookmarkCheck className="w-3.5 h-3.5 mr-1 text-amber-600" />
            ) : (
              <BookmarkPlus className="w-3.5 h-3.5 mr-1 text-slate-400" />
            )}
            {ticket.is_faq ? 'FAQ 추천됨' : 'FAQ 추천'}
          </button>
        )}

        <button
          type="button"
          onClick={onClose}
          className="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};
