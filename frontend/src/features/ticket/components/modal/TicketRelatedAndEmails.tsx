import React, { useState } from 'react';
import { Link2, Mail, ChevronDown, ChevronUp, ArrowUpRight, CheckCircle2 } from 'lucide-react';
import { RelatedTicketItem, EmailNotificationItem } from '../../types/ticket';
import { statusMap } from '../../../../shared/types/common';

export interface TicketRelatedAndEmailsProps {
  relatedTickets?: RelatedTicketItem[];
  emailNotifications?: EmailNotificationItem[];
  onSelectRelatedTicket?: (ticketId: number) => void;
}

export const TicketRelatedAndEmails: React.FC<TicketRelatedAndEmailsProps> = ({
  relatedTickets = [],
  emailNotifications = [],
  onSelectRelatedTicket,
}) => {
  const [showEmails, setShowEmails] = useState(false);
  const [expandedEmailId, setExpandedEmailId] = useState<string | null>(null);

  if (relatedTickets.length === 0 && emailNotifications.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4 pt-2 border-t border-slate-100">
      {/* 1. 유사 문의 연결 섹션 */}
      {relatedTickets.length > 0 && (
        <div className="bg-slate-50/80 border border-slate-200 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2.5">
            <div className="flex items-center space-x-1.5">
              <Link2 className="w-4 h-4 text-indigo-600" />
              <h4 className="text-xs font-bold text-slate-800">유사 문의 및 관련 해결 사례 연결</h4>
            </div>
            <span className="text-[11px] text-slate-400">동일 분류 연관 티켓 {relatedTickets.length}건</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {relatedTickets.map((rt) => {
              const st = statusMap[rt.status] || {
                label: rt.status,
                color: 'bg-slate-100 text-slate-600',
              };
              return (
                <button
                  key={rt.id}
                  type="button"
                  onClick={() => onSelectRelatedTicket && onSelectRelatedTicket(rt.id)}
                  className="text-left p-3 rounded-lg bg-white border border-slate-200 hover:border-indigo-300 hover:shadow-xs transition-all group cursor-pointer flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between gap-1.5 mb-1">
                      <div className="flex items-center space-x-1.5">
                        <span className="text-[10px] font-mono font-bold text-slate-400">
                          {rt.ticket_number}
                        </span>
                        {rt.is_faq && (
                          <span className="px-1.5 py-0.2 bg-amber-100 text-amber-800 text-[10px] font-bold rounded">
                            FAQ
                          </span>
                        )}
                      </div>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${st.color}`}>
                        {st.label}
                      </span>
                    </div>
                    <p className="text-xs font-bold text-slate-800 group-hover:text-indigo-600 transition-colors line-clamp-1">
                      {rt.title}
                    </p>
                    {rt.resolution_summary && (
                      <p className="text-[11px] text-slate-500 mt-1 line-clamp-1">
                        조치: {rt.resolution_summary}
                      </p>
                    )}
                  </div>
                  <div className="mt-2 flex items-center justify-end text-[10px] font-semibold text-indigo-600">
                    <span>문서 이동</span>
                    <ArrowUpRight className="w-3 h-3 ml-0.5" />
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* 2. 모의 이메일 알림 발송 이력 섹션 */}
      {emailNotifications.length > 0 && (
        <div className="bg-slate-50/70 border border-slate-200 rounded-xl overflow-hidden">
          <button
            type="button"
            onClick={() => setShowEmails((prev) => !prev)}
            className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-slate-100/70 transition-colors cursor-pointer"
          >
            <div className="flex items-center space-x-2">
              <Mail className="w-4 h-4 text-indigo-600" />
              <span className="text-xs font-bold text-slate-800">
                이메일 알림 발송 이력 (모의 구현)
              </span>
              <span className="px-2 py-0.5 text-[10px] font-bold bg-indigo-100 text-indigo-700 rounded-full">
                {emailNotifications.length}건 발송됨
              </span>
            </div>
            {showEmails ? (
              <ChevronUp className="w-4 h-4 text-slate-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-400" />
            )}
          </button>

          {showEmails && (
            <div className="px-4 pb-3.5 pt-1 border-t border-slate-200/80 divide-y divide-slate-200/60">
              {emailNotifications.map((mail) => {
                const isExpanded = expandedEmailId === mail.id;
                return (
                  <div key={mail.id} className="py-2.5 text-xs">
                    <div
                      onClick={() => setExpandedEmailId(isExpanded ? null : mail.id)}
                      className="flex items-center justify-between gap-2 cursor-pointer hover:text-indigo-600"
                    >
                      <div className="flex items-center space-x-2 truncate">
                        <span className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 rounded shrink-0">
                          <CheckCircle2 className="w-3 h-3 mr-0.5" />
                          발송완료
                        </span>
                        <span className="font-semibold text-slate-800 truncate">{mail.subject}</span>
                      </div>
                      <span className="text-[11px] text-slate-400 shrink-0">
                        수신: {mail.recipient_email}
                      </span>
                    </div>
                    {isExpanded && (
                      <div className="mt-2 p-3 bg-white rounded-lg border border-slate-200 text-[11px] text-slate-600 whitespace-pre-wrap leading-relaxed">
                        <div className="mb-1.5 pb-1.5 border-b border-slate-100 text-slate-400 flex justify-between">
                          <span>발신: {mail.sender_email}</span>
                          <span>
                            수신: {mail.recipient_name} &lt;{mail.recipient_email}&gt;
                          </span>
                        </div>
                        {mail.body_preview}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
