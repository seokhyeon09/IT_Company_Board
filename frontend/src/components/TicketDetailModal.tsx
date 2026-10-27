import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { apiClient, getErrorMessage } from '../api/client';
import {
  X,
  Clock,
  AlertTriangle,
  CheckCircle2,
  User,
  Calendar,
  Tag,
  FileText,
  ShieldCheck,
  Send,
  Loader2,
  HelpCircle,
} from 'lucide-react';

export interface TicketDetail {
  id: number;
  ticket_number: string;
  title: string;
  category: string;
  content: string;
  status: string;
  priority: string;
  deadline?: string;
  is_overdue: boolean;
  author_id?: any;
  author_name?: string;
  assignee_id?: any;
  assignee_name?: string;
  create_date?: string;
  write_date?: string;
  is_faq: boolean;
  resolution_note?: string;
  rating?: string;
  rating_comment?: string;
}

interface TicketDetailModalProps {
  isOpen: boolean;
  ticketId: number | null;
  onClose: () => void;
  onSuccess?: () => void;
}

const statusMap: Record<string, { label: string; color: string }> = {
  submitted: { label: '접수대기', color: 'bg-amber-50 text-amber-700 border-amber-200' },
  assigned: { label: '배정완료', color: 'bg-blue-50 text-blue-700 border-blue-200' },
  in_progress: { label: '처리중', color: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  pending: { label: '답변대기', color: 'bg-purple-50 text-purple-700 border-purple-200' },
  resolved: { label: '해결완료', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  closed: { label: '종결', color: 'bg-slate-100 text-slate-600 border-slate-200' },
  canceled: { label: '취소', color: 'bg-rose-50 text-rose-700 border-rose-200' },
};

const categoryMap: Record<string, string> = {
  hw: '하드웨어',
  sw: '소프트웨어',
  network: '네트워크',
  account: '계정/권한',
  etc: '기타',
};

const priorityMap: Record<string, { label: string; badge: string }> = {
  '3': { label: '긴급', badge: 'bg-rose-500 text-white' },
  '2': { label: '높음', badge: 'bg-orange-500 text-white' },
  '1': { label: '보통', badge: 'bg-slate-200 text-slate-700' },
  '0': { label: '낮음', badge: 'bg-slate-100 text-slate-500' },
};

function formatHtmlContent(raw: string | undefined | null): string {
  if (!raw) return '';
  return raw
    .replace(/<br\s*[\/]?>/gi, '\n')
    .replace(/<\/p>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .trim();
}

export const TicketDetailModal: React.FC<TicketDetailModalProps> = ({
  isOpen,
  ticketId,
  onClose,
  onSuccess,
}) => {
  const { user } = useAuthStore();
  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState('');

  // Officer Resolution Form State
  const [resolutionNote, setResolutionNote] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [resolveError, setResolveError] = useState('');

  useEffect(() => {
    if (isOpen && ticketId) {
      fetchDetail(ticketId);
      setResolutionNote('');
      setResolveError('');
    } else {
      setTicket(null);
      setFetchError('');
    }
  }, [isOpen, ticketId]);

  const fetchDetail = async (id: number) => {
    setLoading(true);
    setFetchError('');
    try {
      const res = await apiClient.get(`/tickets/${id}`);
      setTicket(res.data);
    } catch (err: any) {
      setFetchError(getErrorMessage(err, '티켓 상세 정보를 불러오는 중 오류가 발생했습니다.'));
    } finally {
      setLoading(false);
    }
  };

  const handleResolveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;

    if (!resolutionNote.trim() || resolutionNote.trim().length < 5) {
      setResolveError('조치 완료 내용은 최소 5자 이상 입력해 주세요.');
      return;
    }

    setSubmitting(true);
    setResolveError('');

    try {
      await apiClient.post(`/tickets/${ticket.id}/resolve`, {
        resolution_note: resolutionNote.trim(),
        if_match_write_date: ticket.write_date,
      });

      // Refresh local detail and trigger dashboard refresh
      await fetchDetail(ticket.id);
      if (onSuccess) {
        onSuccess();
      }
    } catch (err: any) {
      setResolveError(getErrorMessage(err, '해결 완료 처리 중 오류가 발생했습니다.'));
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  const statusInfo = ticket
    ? statusMap[ticket.status] || { label: ticket.status, color: 'bg-slate-100 text-slate-700' }
    : { label: '', color: '' };

  const priorityInfo = ticket
    ? priorityMap[ticket.priority] || { label: '보통', badge: 'bg-slate-200 text-slate-700' }
    : { label: '', badge: '' };

  const isResolvedOrClosed = ticket?.status === 'resolved' || ticket?.status === 'closed';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col overflow-hidden border border-slate-100">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center space-x-3">
            {ticket && (
              <>
                <span className="font-mono text-xs font-bold text-slate-600 bg-white border border-slate-200 px-2.5 py-1 rounded-md shadow-xs">
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
                    <HelpCircle className="w-3 h-3 mr-1" /> FAQ
                  </span>
                )}
              </>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-sm text-slate-700">
          {loading ? (
            <div className="py-20 text-center text-slate-400 flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mb-3" />
              티켓 상세 정보를 불러오는 중입니다...
            </div>
          ) : fetchError ? (
            <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-center">
              <p className="font-bold">오류</p>
              <p className="text-xs mt-1">{fetchError}</p>
            </div>
          ) : ticket ? (
            <>
              {/* Title & Metadata Grid */}
              <div>
                <h2 className="text-xl font-bold text-slate-900 tracking-tight leading-snug">
                  {ticket.title}
                </h2>

                <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-100 text-xs">
                  <div>
                    <span className="text-slate-400 flex items-center mb-1">
                      <User className="w-3.5 h-3.5 mr-1" /> 작성자
                    </span>
                    <span className="font-semibold text-slate-800">
                      {ticket.author_name || '사원'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 flex items-center mb-1">
                      <Tag className="w-3.5 h-3.5 mr-1" /> 카테고리
                    </span>
                    <span className="font-semibold text-slate-800">
                      {categoryMap[ticket.category] || ticket.category}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 flex items-center mb-1">
                      <ShieldCheck className="w-3.5 h-3.5 mr-1" /> 담당자
                    </span>
                    <span className="font-semibold text-slate-800">
                      {ticket.assignee_name || '배정 대기'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 flex items-center mb-1">
                      <Calendar className="w-3.5 h-3.5 mr-1" /> 접수일시
                    </span>
                    <span className="font-semibold text-slate-800">
                      {ticket.create_date ? ticket.create_date.substring(0, 16).replace('T', ' ') : '-'}
                    </span>
                  </div>
                </div>

                {/* SLA Warning Banner */}
                {ticket.deadline && (
                  <div
                    className={`mt-3 flex items-center justify-between px-3.5 py-2 rounded-xl text-xs border ${
                      ticket.is_overdue
                        ? 'bg-rose-50 border-rose-200 text-rose-700'
                        : 'bg-amber-50 border-amber-200 text-amber-800'
                    }`}
                  >
                    <div className="flex items-center font-medium">
                      {ticket.is_overdue ? (
                        <AlertTriangle className="w-4 h-4 mr-1.5 text-rose-600" />
                      ) : (
                        <Clock className="w-4 h-4 mr-1.5 text-amber-600" />
                      )}
                      <span>SLA 조치 기한: {ticket.deadline.substring(0, 16).replace('T', ' ')}</span>
                    </div>
                    {ticket.is_overdue && (
                      <span className="font-bold text-rose-700 bg-rose-100 px-2 py-0.5 rounded">
                        기한 초과
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* Inquiry Content */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center">
                  <FileText className="w-3.5 h-3.5 mr-1" /> 문의 상세 내용
                </h4>
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 whitespace-pre-wrap leading-relaxed text-sm min-h-[100px]">
                  {formatHtmlContent(ticket.content) || '작성된 상세 내용이 없습니다.'}
                </div>
              </div>

              {/* Resolution Area: Display note if resolved */}
              {ticket.resolution_note && (
                <div className="p-4 bg-emerald-50/80 border border-emerald-200 rounded-xl">
                  <div className="flex items-center text-emerald-800 font-bold text-xs uppercase tracking-wider mb-2">
                    <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-600" />
                    IT 담당자 조치 내용
                  </div>
                  <div className="text-emerald-950 text-sm whitespace-pre-wrap leading-relaxed">
                    {formatHtmlContent(ticket.resolution_note)}
                  </div>
                </div>
              )}

              {/* IT Officer Action Form (Only when NOT resolved and user is officer) */}
              {!isResolvedOrClosed && user?.is_officer && (
                <div className="pt-4 border-t border-slate-200">
                  <div className="flex items-center space-x-1.5 mb-2">
                    <ShieldCheck className="w-4 h-4 text-indigo-600" />
                    <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      IT 담당자 해결 조치 등록
                    </h4>
                  </div>

                  <form onSubmit={handleResolveSubmit} className="space-y-3">
                    <textarea
                      rows={3}
                      value={resolutionNote}
                      onChange={(e) => setResolutionNote(e.target.value)}
                      placeholder="처리 완료된 구체적인 조치 내용(예: 부품 교체 완료, 원격 세팅 지원 등)을 최소 5자 이상 입력하세요..."
                      className="w-full px-3.5 py-2.5 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
                    />

                    {resolveError && (
                      <div className="text-xs text-rose-600 bg-rose-50 border border-rose-200 p-2.5 rounded-lg">
                        {resolveError}
                      </div>
                    )}

                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={submitting}
                        className="flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-md shadow-emerald-600/20 disabled:opacity-50 transition-all"
                      >
                        {submitting ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                            처리 중...
                          </>
                        ) : (
                          <>
                            <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                            해결 완료 처리
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {/* Regular User Pending Message */}
              {!isResolvedOrClosed && !user?.is_officer && (
                <div className="p-3.5 bg-blue-50 border border-blue-200 rounded-xl text-blue-800 text-xs flex items-center">
                  <Clock className="w-4 h-4 mr-2 text-blue-600 shrink-0" />
                  <span>현재 IT 지원팀에서 담당자 배정 및 문의 처리를 진행 중입니다.</span>
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 transition-all"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
};
