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
  Loader2,
  HelpCircle,
  Star,
  BookmarkPlus,
  BookmarkCheck,
  History,
  RotateCcw,
  Edit3,
  MessageSquare,
} from 'lucide-react';

export interface TicketLog {
  id: number;
  date?: string;
  author_name?: string;
  body: string;
  message_type?: string;
}

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
  logs?: TicketLog[];
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
  const [submittingResolve, setSubmittingResolve] = useState(false);
  const [resolveError, setResolveError] = useState('');

  // Officer Edit Resolution State (답변 수정)
  const [isEditingResolution, setIsEditingResolution] = useState(false);
  const [editResolutionNote, setEditResolutionNote] = useState('');
  const [submittingEditResolution, setSubmittingEditResolution] = useState(false);
  const [editResolutionError, setEditResolutionError] = useState('');

  // Employee Restart/Follow-up Inquiry State (직원 재문의)
  const [showRestartForm, setShowRestartForm] = useState(false);
  const [restartReason, setRestartReason] = useState('');
  const [submittingRestart, setSubmittingRestart] = useState(false);
  const [restartError, setRestartError] = useState('');

  // Rating State
  const [ratingScore, setRatingScore] = useState<number>(5);
  const [ratingComment, setRatingComment] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);
  const [ratingError, setRatingError] = useState('');

  // FAQ Toggle State
  const [togglingFaq, setTogglingFaq] = useState(false);

  useEffect(() => {
    if (isOpen && ticketId) {
      fetchDetail(ticketId);
      setResolutionNote('');
      setResolveError('');
      setIsEditingResolution(false);
      setEditResolutionNote('');
      setEditResolutionError('');
      setShowRestartForm(false);
      setRestartReason('');
      setRestartError('');
      setRatingScore(5);
      setRatingComment('');
      setRatingError('');
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

    setSubmittingResolve(true);
    setResolveError('');

    try {
      await apiClient.post(`/tickets/${ticket.id}/resolve`, {
        resolution_note: resolutionNote.trim(),
        if_match_write_date: ticket.write_date,
      });

      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setResolveError(getErrorMessage(err, '해결 완료 처리 중 오류가 발생했습니다.'));
    } finally {
      setSubmittingResolve(false);
    }
  };

  // Officer 답변 수정 핸들러
  const handleUpdateResolutionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;

    if (!editResolutionNote.trim() || editResolutionNote.trim().length < 5) {
      setEditResolutionError('수정할 조치 내용은 최소 5자 이상 입력해 주세요.');
      return;
    }

    setSubmittingEditResolution(true);
    setEditResolutionError('');

    try {
      await apiClient.post(`/tickets/${ticket.id}/update-resolution`, {
        resolution_note: editResolutionNote.trim(),
        if_match_write_date: ticket.write_date,
      });

      setIsEditingResolution(false);
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setEditResolutionError(getErrorMessage(err, '답변 수정 처리 중 오류가 발생했습니다.'));
    } finally {
      setSubmittingEditResolution(false);
    }
  };

  // Employee 재문의 핸들러
  const handleRestartSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;

    if (!restartReason.trim() || restartReason.trim().length < 5) {
      setRestartError('재문의 내용은 최소 5자 이상 입력해 주세요.');
      return;
    }

    setSubmittingRestart(true);
    setRestartError('');

    try {
      await apiClient.post(`/tickets/${ticket.id}/restart`, {
        reason: restartReason.trim(),
      });

      setShowRestartForm(false);
      setRestartReason('');
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setRestartError(getErrorMessage(err, '재문의 등록 중 오류가 발생했습니다.'));
    } finally {
      setSubmittingRestart(false);
    }
  };

  const handleRateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;

    setSubmittingRating(true);
    setRatingError('');

    try {
      await apiClient.post(`/tickets/${ticket.id}/rate`, {
        rating: String(ratingScore),
        rating_comment: ratingComment.trim() || undefined,
        if_match_write_date: ticket.write_date,
      });

      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setRatingError(getErrorMessage(err, '만족도 평가 등록 중 오류가 발생했습니다.'));
    } finally {
      setSubmittingRating(false);
    }
  };

  const handleToggleFaq = async () => {
    if (!ticket) return;
    setTogglingFaq(true);
    try {
      await apiClient.post(`/tickets/${ticket.id}/toggle-faq`);
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      alert(getErrorMessage(err, 'FAQ 설정 변경 중 오류가 발생했습니다.'));
    } finally {
      setTogglingFaq(false);
    }
  };

  if (!isOpen) return null;

  const statusInfo = ticket
    ? statusMap[ticket.status] || { label: ticket.status, color: 'bg-slate-100 text-slate-700' }
    : { label: '', color: '' };

  const priorityInfo = ticket
    ? priorityMap[ticket.priority] || { label: '보통', badge: 'bg-slate-200 text-slate-700' }
    : { label: '', badge: '' };

  const isResolved = ticket?.status === 'resolved';
  const isClosed = ticket?.status === 'closed';
  const isAuthor = ticket && user && ticket.author_id === user.uid;

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
                    <HelpCircle className="w-3 h-3 mr-1" /> FAQ 공식 선정
                  </span>
                )}
              </>
            )}
          </div>

          <div className="flex items-center space-x-2">
            {/* Officer FAQ Toggle Action */}
            {user?.is_officer && ticket && ticket.resolution_note && (
              <button
                type="button"
                onClick={handleToggleFaq}
                disabled={togglingFaq}
                className={`flex items-center px-2.5 py-1.5 rounded-lg text-xs font-semibold border transition-all cursor-pointer ${
                  ticket.is_faq
                    ? 'bg-indigo-50 text-indigo-700 border-indigo-300 hover:bg-indigo-100'
                    : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                }`}
                title="FAQ 지식창고 등록/해제"
              >
                {ticket.is_faq ? (
                  <>
                    <BookmarkCheck className="w-3.5 h-3.5 mr-1 text-indigo-600" />
                    FAQ 등록됨
                  </>
                ) : (
                  <>
                    <BookmarkPlus className="w-3.5 h-3.5 mr-1 text-slate-400" />
                    FAQ 추천
                  </>
                )}
              </button>
            )}

            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-all cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
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
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-slate-800 whitespace-pre-wrap leading-relaxed text-sm min-h-[90px]">
                  {formatHtmlContent(ticket.content) || '작성된 상세 내용이 없습니다.'}
                </div>
              </div>

              {/* Resolution Area: Display note with edit button for officer */}
              {ticket.resolution_note && (
                <div className="p-4 bg-emerald-50/80 border border-emerald-200 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center text-emerald-800 font-bold text-xs uppercase tracking-wider">
                      <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-600" />
                      IT 담당자 조치 내용
                    </div>
                    {user?.is_officer && !isEditingResolution && (
                      <button
                        type="button"
                        onClick={() => {
                          setEditResolutionNote(formatHtmlContent(ticket.resolution_note));
                          setIsEditingResolution(true);
                          setEditResolutionError('');
                        }}
                        className="flex items-center text-xs font-semibold text-emerald-700 hover:text-emerald-900 bg-white border border-emerald-300 hover:bg-emerald-100/50 px-2.5 py-1 rounded-lg transition-all cursor-pointer shadow-xs"
                      >
                        <Edit3 className="w-3.5 h-3.5 mr-1" />
                        답변 수정
                      </button>
                    )}
                  </div>

                  {isEditingResolution ? (
                    <form onSubmit={handleUpdateResolutionSubmit} className="space-y-3 mt-3">
                      <textarea
                        rows={3}
                        value={editResolutionNote}
                        onChange={(e) => setEditResolutionNote(e.target.value)}
                        className="w-full px-3.5 py-2.5 text-xs border border-emerald-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none text-slate-800"
                        placeholder="수정할 조치 내용을 입력하세요 (최소 5자)..."
                      />
                      {editResolutionError && (
                        <p className="text-xs text-rose-600 font-medium">{editResolutionError}</p>
                      )}
                      <div className="flex justify-end space-x-2">
                        <button
                          type="button"
                          onClick={() => setIsEditingResolution(false)}
                          className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
                        >
                          취소
                        </button>
                        <button
                          type="submit"
                          disabled={submittingEditResolution}
                          className="flex items-center px-3.5 py-1.5 text-xs font-semibold text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-all cursor-pointer"
                        >
                          {submittingEditResolution ? (
                            <>
                              <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                              저장 중...
                            </>
                          ) : (
                            '수정 저장'
                          )}
                        </button>
                      </div>
                    </form>
                  ) : (
                    <div className="text-emerald-950 text-sm whitespace-pre-wrap leading-relaxed">
                      {formatHtmlContent(ticket.resolution_note)}
                    </div>
                  )}
                </div>
              )}

              {/* Employee Follow-up Inquiry (재문의) Section */}
              {isAuthor && ['pending', 'resolved', 'closed'].includes(ticket.status) && (
                <div className="p-4 bg-purple-50/70 border border-purple-200 rounded-xl">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1.5">
                      <RotateCcw className="w-4 h-4 text-purple-600" />
                      <span className="text-xs font-bold text-purple-900 uppercase tracking-wider">
                        추가 문의 (재문의)
                      </span>
                    </div>
                    {!showRestartForm && (
                      <button
                        type="button"
                        onClick={() => {
                          setShowRestartForm(true);
                          setRestartReason('');
                          setRestartError('');
                        }}
                        className="flex items-center px-3 py-1.5 text-xs font-semibold text-purple-700 bg-white border border-purple-300 rounded-lg hover:bg-purple-100/50 transition-all cursor-pointer shadow-xs"
                      >
                        <MessageSquare className="w-3.5 h-3.5 mr-1" />
                        추가 재문의하기
                      </button>
                    )}
                  </div>

                  {showRestartForm ? (
                    <form onSubmit={handleRestartSubmit} className="space-y-3 mt-3">
                      <p className="text-xs text-purple-800">
                        조치 내용에 대해 미해결된 사항이나 추가 문의사항을 남겨주시면 담당자에게 재배정되어 처리가 다시 시작됩니다.
                      </p>
                      <textarea
                        rows={3}
                        value={restartReason}
                        onChange={(e) => setRestartReason(e.target.value)}
                        placeholder="추가 문의하실 상세 내용을 입력하세요 (최소 5자)..."
                        className="w-full px-3.5 py-2.5 text-xs border border-purple-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none text-slate-800"
                      />
                      {restartError && (
                        <p className="text-xs text-rose-600 font-medium">{restartError}</p>
                      )}
                      <div className="flex justify-end space-x-2">
                        <button
                          type="button"
                          onClick={() => setShowRestartForm(false)}
                          className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
                        >
                          취소
                        </button>
                        <button
                          type="submit"
                          disabled={submittingRestart}
                          className="flex items-center px-4 py-1.5 text-xs font-semibold text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-all cursor-pointer"
                        >
                          {submittingRestart ? (
                            <>
                              <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                              등록 중...
                            </>
                          ) : (
                            '재문의 등록'
                          )}
                        </button>
                      </div>
                    </form>
                  ) : (
                    <p className="text-xs text-purple-700 mt-1">
                      조치가 완료되었거나 추가 확인이 필요한 경우 언제든지 재문의를 통해 다시 처리를 요청하실 수 있습니다.
                    </p>
                  )}
                </div>
              )}

              {/* Customer Rating Section (If already rated) */}
              {ticket.rating && ticket.rating !== '0' && (
                <div className="p-4 bg-amber-50/70 border border-amber-200 rounded-xl">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-1.5">
                      <span className="text-xs font-bold text-amber-900 uppercase tracking-wider">
                        직원 만족도 평가 결과
                      </span>
                    </div>
                    <div className="flex items-center space-x-1">
                      {[1, 2, 3, 4, 5].map((starVal) => (
                        <Star
                          key={starVal}
                          className={`w-4 h-4 ${
                            starVal <= Number(ticket.rating)
                              ? 'text-amber-500 fill-amber-400'
                              : 'text-slate-300'
                          }`}
                        />
                      ))}
                      <span className="text-xs font-black text-amber-900 ml-1.5">
                        {ticket.rating}점 / 5점
                      </span>
                    </div>
                  </div>
                  {ticket.rating_comment && (
                    <p className="text-xs text-amber-950 mt-1 italic bg-white/70 p-2.5 rounded-lg border border-amber-100">
                      "{ticket.rating_comment}"
                    </p>
                  )}
                </div>
              )}

              {/* Active Rating Form: When resolved, author hasn't rated yet */}
              {isResolved && isAuthor && (!ticket.rating || ticket.rating === '0') && (
                <div className="p-4 bg-indigo-50/70 border border-indigo-200 rounded-xl">
                  <div className="flex items-center space-x-1.5 mb-2">
                    <Star className="w-4 h-4 text-indigo-600 fill-indigo-500" />
                    <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wider">
                      조치 만족도 평가 (본인 평가 후 종결)
                    </h4>
                  </div>
                  <p className="text-xs text-slate-500 mb-3">
                    IT 지원팀의 조치 내용에 대해 만족도를 평가해 주세요. 평가 완료 시 문의가 최종 종결됩니다.
                  </p>

                  <form onSubmit={handleRateSubmit} className="space-y-3">
                    <div className="flex items-center space-x-2 bg-white p-2.5 rounded-xl border border-indigo-100 w-fit">
                      <span className="text-xs text-slate-600 font-semibold mr-1">별점:</span>
                      {[1, 2, 3, 4, 5].map((s) => (
                        <button
                          key={s}
                          type="button"
                          onClick={() => setRatingScore(s)}
                          className="p-1 hover:scale-110 transition-transform cursor-pointer"
                        >
                          <Star
                            className={`w-5 h-5 ${
                              s <= ratingScore
                                ? 'text-amber-500 fill-amber-400'
                                : 'text-slate-200'
                            }`}
                          />
                        </button>
                      ))}
                      <span className="text-xs font-bold text-amber-600 ml-1">
                        {ratingScore}점
                      </span>
                    </div>

                    <textarea
                      rows={2}
                      value={ratingComment}
                      onChange={(e) => setRatingComment(e.target.value)}
                      placeholder="처리 과정에 대한 한줄평이나 감사의견을 남겨주세요 (선택사항)"
                      className="w-full px-3.5 py-2 text-xs border border-slate-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                    />

                    {ratingError && (
                      <div className="text-xs text-rose-600 bg-rose-50 border border-rose-200 p-2.5 rounded-lg">
                        {ratingError}
                      </div>
                    )}

                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={submittingRating}
                        className="flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl shadow-md shadow-indigo-600/20 disabled:opacity-50 transition-all cursor-pointer"
                      >
                        {submittingRating ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                            제출 중...
                          </>
                        ) : (
                          <>
                            <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                            만족도 제출 및 문의 종결
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {/* IT Officer Action Form (Only when NOT resolved/closed and user is officer) */}
              {!isResolved && !isClosed && user?.is_officer && (
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
                        disabled={submittingResolve}
                        className="flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-md shadow-emerald-600/20 disabled:opacity-50 transition-all cursor-pointer"
                      >
                        {submittingResolve ? (
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
              {!isResolved && !isClosed && !user?.is_officer && (
                <div className="p-3.5 bg-blue-50 border border-blue-200 rounded-xl text-blue-800 text-xs flex items-center">
                  <Clock className="w-4 h-4 mr-2 text-blue-600 shrink-0" />
                  <span>현재 IT 지원팀에서 담당자 배정 및 문의 처리를 진행 중입니다.</span>
                </div>
              )}

              {/* Officer-Only Activity & Audit Logs Section */}
              {user?.is_officer && ticket.logs && ticket.logs.length > 0 && (
                <div className="pt-4 border-t border-slate-200">
                  <div className="flex items-center space-x-1.5 mb-3">
                    <History className="w-4 h-4 text-slate-500" />
                    <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                      IT 담당자 활동 및 처리 이력 ({ticket.logs.length}건)
                    </h4>
                    <span className="text-[10px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded border border-slate-200">
                      사원 비노출
                    </span>
                  </div>
                  <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                    {ticket.logs.map((log) => (
                      <div
                        key={log.id}
                        className="p-3 bg-slate-50 border border-slate-200/80 rounded-xl text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between text-slate-500 text-[11px]">
                          <span className="font-semibold text-slate-700">{log.author_name}</span>
                          <span>{log.date ? log.date.substring(0, 16).replace('T', ' ') : '-'}</span>
                        </div>
                        <p className="text-slate-800 whitespace-pre-wrap leading-relaxed">{log.body}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
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
