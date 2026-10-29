import React from 'react';
import {
  X,
  HelpCircle,
  BookmarkPlus,
  BookmarkCheck,
  Loader2,
} from 'lucide-react';
import { TicketDetail } from '../../types/ticket';
import { statusMap, priorityMap } from '../../../../shared/types/common';

interface TicketHeaderProps {
  ticket: TicketDetail | null;
  isOfficer: boolean;
  togglingFaq: boolean;
  onToggleFaq: () => void;
  onClose: () => void;
}

export const TicketHeader: React.FC<TicketHeaderProps> = ({
  ticket,
  isOfficer,
  togglingFaq,
  onToggleFaq,
  onClose,
}) => {
  const statusInfo = ticket
    ? statusMap[ticket.status] || {
        label: ticket.status,
        color: 'bg-slate-100 text-slate-700 border-slate-200',
      }
    : { label: '', color: '' };
  const priorityInfo = ticket
    ? priorityMap[ticket.priority] || {
        label: '보통',
        badge: 'bg-slate-200 text-slate-700',
      }
    : { label: '', badge: '' };

  return (
    <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
      <div className="flex items-center space-x-3">
        {ticket && (
          <>
            <span
              data-testid="modal-ticket-number"
              className="font-mono text-xs font-bold text-slate-600 bg-white border border-slate-200 px-2.5 py-1 rounded-md shadow-xs"
            >
              {ticket.ticket_number}
            </span>
            <span className={`text-xs px-2.5 py-1 rounded-full border font-semibold ${statusInfo.color}`}>
              {statusInfo.label}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded font-semibold ${priorityInfo.badge}`}>
              {priorityInfo.label}
            </span>
            {ticket.is_faq && (
              <span className="flex items-center text-xs bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded font-medium">
                <HelpCircle className="w-3 h-3 mr-1" /> FAQ 공식 선정
              </span>
            )}
          </>
        )}
      </div>

      <div className="flex items-center space-x-2">
        {isOfficer && ticket && ticket.resolution_note && (
          <button
            type="button"
            onClick={onToggleFaq}
            disabled={togglingFaq}
            className={`flex items-center px-2.5 py-1.5 rounded-lg text-xs font-semibold border transition-all cursor-pointer ${
              ticket.is_faq
                ? 'bg-indigo-50 text-indigo-700 border-indigo-300 hover:bg-indigo-100'
                : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
            }`}
            title="FAQ 지식창고 등록/해제"
          >
            {togglingFaq ? (
              <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
            ) : ticket.is_faq ? (
              <BookmarkCheck className="w-3.5 h-3.5 mr-1 text-indigo-600" />
            ) : (
              <BookmarkPlus className="w-3.5 h-3.5 mr-1 text-slate-400" />
            )}
            {ticket.is_faq ? 'FAQ 등록됨' : 'FAQ 추천'}
          </button>
        )}

        <button
          type="button"
          onClick={onClose}
          className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-all cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};
