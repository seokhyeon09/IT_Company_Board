import React from 'react';
import { Send, ExternalLink, CheckCircle2 } from 'lucide-react';
import { EmailNotificationItem } from '../../ticket/types/ticket';
import { formatMailDate } from './EmailList';

interface EmailPreviewProps {
  mail: EmailNotificationItem;
  onOpenTicket: (ticketId: number) => void;
}

export const EmailPreview: React.FC<EmailPreviewProps> = ({ mail, onOpenTicket }) => (
  <div className="space-y-4">
    <div className="bg-white p-4 rounded-xl border border-slate-200 space-y-2.5">
      <div className="flex items-center justify-between">
        <span className="inline-flex items-center text-[11px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
          <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
          {mail.status}
        </span>
        <span className="text-xs font-mono text-slate-400">{mail.ticket_number}</span>
      </div>
      <h3 className="text-sm font-bold text-slate-900 leading-snug">{mail.subject}</h3>
      <div className="pt-2 border-t border-slate-100 text-xs space-y-1 text-slate-600">
        <div className="flex justify-between">
          <span className="text-slate-400">발신자:</span>
          <span className="font-mono text-[11px]">{mail.sender_email}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">수신자:</span>
          <span className="font-semibold text-slate-800">
            {mail.recipient_name} &lt;{mail.recipient_email}&gt;
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">발송 일시:</span>
          <span>{formatMailDate(mail.sent_at)}</span>
        </div>
      </div>
    </div>

    <div className="bg-white p-4 rounded-xl border border-slate-200">
      <div className="flex items-center space-x-1.5 text-[11px] font-bold text-slate-400 uppercase mb-2">
        <Send className="w-3.5 h-3.5" />
        <span>이메일 본문 미리보기</span>
      </div>
      <div className="text-xs text-slate-700 whitespace-pre-wrap leading-relaxed bg-slate-50 p-3.5 rounded-lg border border-slate-100">
        {mail.body_preview}
      </div>
    </div>

    <div className="flex justify-end">
      <button
        type="button"
        onClick={() => onOpenTicket(mail.ticket_id)}
        className="inline-flex items-center px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl transition-colors cursor-pointer"
      >
        <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
        해당 문의 상세 보기 ({mail.ticket_number})
      </button>
    </div>
  </div>
);
