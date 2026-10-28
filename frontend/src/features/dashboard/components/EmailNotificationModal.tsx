import React, { useEffect, useState } from 'react';
import {
  X,
  Mail,
  Send,
  ExternalLink,
  Loader2,
  CheckCircle2,
  Inbox,
} from 'lucide-react';
import { apiClient, getErrorMessage } from '../../../api/client';
import { EmailNotificationItem } from '../../ticket/types/ticket';

export interface EmailNotificationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTicket: (ticketId: number) => void;
}

const EVENT_BADGE_MAP: Record<string, { label: string; className: string }> = {
  created: { label: '접수 확인', className: 'bg-slate-100 text-slate-700 border-slate-200' },
  assigned: { label: '담당자 배정', className: 'bg-blue-50 text-blue-700 border-blue-200' },
  pending_request: { label: '답변 대기 요청', className: 'bg-purple-50 text-purple-700 border-purple-200' },
  resolved: { label: '조치 완료 안내', className: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  follow_up: { label: '추가 회신 알림', className: 'bg-amber-50 text-amber-800 border-amber-200' },
};

export const EmailNotificationModal: React.FC<EmailNotificationModalProps> = ({
  isOpen,
  onClose,
  onSelectTicket,
}) => {
  const [items, setItems] = useState<EmailNotificationItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<EmailNotificationItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    const fetchNotifications = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.get('/tickets/notifications', { params: { limit: 30 } });
        const list: EmailNotificationItem[] = res.data.data || [];
        setItems(list);
        setSelectedItem(list.length > 0 ? list[0] : null);
      } catch (err: any) {
        setError(getErrorMessage(err, '모의 이메일 알림 내역을 불러오지 못했습니다.'));
      } finally {
        setLoading(false);
      }
    };
    fetchNotifications();
  }, [isOpen]);

  if (!isOpen) return null;

  const formatDate = (iso?: string) => {
    if (!iso) return '-';
    return new Date(iso).toLocaleString('ko-KR', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[88vh] flex flex-col overflow-hidden border border-slate-100">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-indigo-600 text-white rounded-xl shadow-xs">
              <Mail className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-bold text-slate-900">이메일 알림 발송 내역 (모의 구현)</h2>
                <span className="px-2 py-0.5 text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-full">
                  Mock SMTP
                </span>
              </div>
              <p className="text-xs text-slate-500">
                문의 접수, 담당자 배정, 답변 요청 및 조치 완료 시 발송되는 자동 이메일 알림 로그입니다.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/60 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-hidden flex flex-col md:flex-row min-h-[420px]">
          {loading ? (
            <div className="w-full py-20 text-center text-slate-400 flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mb-3" />
              이메일 발송 로그를 불러오는 중입니다...
            </div>
          ) : error ? (
            <div className="w-full p-6 text-center text-rose-700 text-xs font-semibold">{error}</div>
          ) : items.length === 0 ? (
            <div className="w-full py-20 text-center text-slate-400 flex flex-col items-center justify-center">
              <Inbox className="w-10 h-10 text-slate-300 mb-2" />
              <p className="text-sm font-semibold text-slate-600">발송된 모의 이메일 내역이 없습니다.</p>
            </div>
          ) : (
            <>
              {/* Left List */}
              <div className="w-full md:w-5/12 border-b md:border-b-0 md:border-r border-slate-200 overflow-y-auto divide-y divide-slate-100 max-h-60 md:max-h-none">
                {items.map((item) => {
                  const badge = EVENT_BADGE_MAP[item.event_type] || EVENT_BADGE_MAP.created;
                  const isSelected = selectedItem?.id === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setSelectedItem(item)}
                      className={`w-full text-left p-3.5 transition-colors cursor-pointer ${
                        isSelected ? 'bg-indigo-50/70' : 'hover:bg-slate-50'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${badge.className}`}
                        >
                          {badge.label}
                        </span>
                        <span className="text-[11px] text-slate-400">{formatDate(item.sent_at)}</span>
                      </div>
                      <p className="text-xs font-bold text-slate-800 line-clamp-1">{item.subject}</p>
                      <p className="text-[11px] text-slate-500 mt-0.5 truncate">
                        수신: {item.recipient_name} ({item.recipient_email})
                      </p>
                    </button>
                  );
                })}
              </div>

              {/* Right Preview Pane */}
              <div className="w-full md:w-7/12 p-5 overflow-y-auto bg-slate-50/40 flex flex-col justify-between">
                {selectedItem ? (
                  <div className="space-y-4">
                    <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-2.5">
                      <div className="flex items-center justify-between">
                        <span className="inline-flex items-center text-[11px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
                          <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                          {selectedItem.status}
                        </span>
                        <span className="text-xs font-mono text-slate-400">
                          {selectedItem.ticket_number}
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-slate-900 leading-snug">
                        {selectedItem.subject}
                      </h3>
                      <div className="pt-2 border-t border-slate-100 text-xs space-y-1 text-slate-600">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 font-medium">발신자:</span>
                          <span className="font-mono text-[11px]">{selectedItem.sender_email}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 font-medium">수신자:</span>
                          <span className="font-semibold text-slate-800">
                            {selectedItem.recipient_name} &lt;{selectedItem.recipient_email}&gt;
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 font-medium">발송 일시:</span>
                          <span>{formatDate(selectedItem.sent_at)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
                      <div className="flex items-center space-x-1.5 text-[11px] font-bold text-slate-400 uppercase mb-2">
                        <Send className="w-3.5 h-3.5" />
                        <span>이메일 본문 미리보기</span>
                      </div>
                      <div className="text-xs text-slate-700 whitespace-pre-wrap leading-relaxed bg-slate-50 p-3.5 rounded-lg border border-slate-100">
                        {selectedItem.body_preview}
                      </div>
                    </div>

                    <div className="flex justify-end">
                      <button
                        type="button"
                        onClick={() => {
                          const targetId = selectedItem.ticket_id;
                          onClose();
                          onSelectTicket(targetId);
                        }}
                        className="inline-flex items-center px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-xs transition-colors cursor-pointer"
                      >
                        <ExternalLink className="w-3.5 h-3.5 mr-1.5" />
                        해당 문의 상세 보기 ({selectedItem.ticket_number})
                      </button>
                    </div>
                  </div>
                ) : null}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 transition-all cursor-pointer"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
};
