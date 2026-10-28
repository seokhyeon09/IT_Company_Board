import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../../stores/authStore';
import { apiClient, getErrorMessage } from '../../../api/client';
import { Loader2 } from 'lucide-react';
import { TicketDetail, Attachment } from '../types/ticket';
import { formatHtmlContent } from '../../../shared/utils/htmlUtils';

import { TicketHeader } from './modal/TicketHeader';
import { TicketMainContent } from './modal/TicketMainContent';
import { TicketAttachments } from './modal/TicketAttachments';
import { TicketWorkflowBar } from './modal/TicketWorkflowBar';
import { TicketTimeline } from './modal/TicketTimeline';
import { TicketActionForms } from './modal/TicketActionForms';
import { TicketOfficerLogs } from './modal/TicketOfficerLogs';

export interface TicketDetailModalProps {
  isOpen: boolean;
  ticketId: number | null;
  onClose: () => void;
  onSuccess?: () => void;
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

  // 1. Resolve State
  const [resolutionNote, setResolutionNote] = useState('');
  const [submittingResolve, setSubmittingResolve] = useState(false);
  const [resolveError, setResolveError] = useState('');

  // 2. Edit Resolution State
  const [isEditingResolution, setIsEditingResolution] = useState(false);
  const [editResolutionNote, setEditResolutionNote] = useState('');
  const [submittingEditResolution, setSubmittingEditResolution] = useState(false);
  const [editResolutionError, setEditResolutionError] = useState('');

  // 3. Restart Inquiry State
  const [showRestartForm, setShowRestartForm] = useState(false);
  const [restartReason, setRestartReason] = useState('');
  const [submittingRestart, setSubmittingRestart] = useState(false);
  const [restartError, setRestartError] = useState('');

  // 4. Rating State
  const [ratingScore, setRatingScore] = useState<number>(5);
  const [ratingComment, setRatingComment] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);
  const [ratingError, setRatingError] = useState('');

  // 5. Inquiry Edit State (submitted)
  const [isEditingTicket, setIsEditingTicket] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editCategory, setEditCategory] = useState('');
  const [editPriority, setEditPriority] = useState('');
  const [editContent, setEditContent] = useState('');
  const [submittingEditTicket, setSubmittingEditTicket] = useState(false);
  const [editTicketError, setEditTicketError] = useState('');

  // 6. Attachment State
  const [uploadingAttachment, setUploadingAttachment] = useState(false);
  const [downloadingAttachmentId, setDownloadingAttachmentId] = useState<number | null>(null);

  // 7. Workflow State
  const [transitioningStatus, setTransitioningStatus] = useState<string | null>(null);
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [closeNote, setCloseNote] = useState('');
  const [submittingClose, setSubmittingClose] = useState(false);
  const [closeError, setCloseError] = useState('');

  // 8. Pending State
  const [showPendingModal, setShowPendingModal] = useState(false);
  const [pendingReason, setPendingReason] = useState('');
  const [submittingPending, setSubmittingPending] = useState(false);
  const [pendingError, setPendingError] = useState('');

  // 9. Pending Reply State
  const [showPendingReplyForm, setShowPendingReplyForm] = useState(false);
  const [pendingReplyText, setPendingReplyText] = useState('');
  const [submittingPendingReply, setSubmittingPendingReply] = useState(false);
  const [pendingReplyError, setPendingReplyError] = useState('');

  // 10. Cancel State
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [submittingCancel, setSubmittingCancel] = useState(false);
  const [cancelError, setCancelError] = useState('');

  // 11. FAQ Toggle State
  const [togglingFaq, setTogglingFaq] = useState(false);

  useEffect(() => {
    if (isOpen && ticketId) {
      fetchDetail(ticketId);
      resetForms();
    }
  }, [isOpen, ticketId]);

  const resetForms = () => {
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
    setShowCloseModal(false);
    setCloseNote('');
    setCloseError('');
    setShowPendingModal(false);
    setPendingReason('');
    setPendingError('');
    setShowPendingReplyForm(false);
    setPendingReplyText('');
    setPendingReplyError('');
    setShowCancelModal(false);
    setIsEditingTicket(false);
    setEditTitle('');
    setEditCategory('');
    setEditPriority('');
    setEditContent('');
    setEditTicketError('');
  };

  const fetchDetail = async (id: number) => {
    setLoading(true);
    setFetchError('');
    try {
      const res = await apiClient.get<TicketDetail>(`/tickets/${id}`);
      setTicket(res.data);
    } catch (err: any) {
      setFetchError(getErrorMessage(err, '티켓 상세 정보를 불러오지 못했습니다.'));
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const isAuthor = Boolean(
    ticket &&
      user &&
      (ticket.author_id === user.uid ||
        String(ticket.author_id) === String(user.uid) ||
        (Array.isArray(ticket.author_id) && String(ticket.author_id[0]) === String(user.uid)) ||
        (ticket.author_name && user.name && ticket.author_name === user.name))
  );
  const isOfficer = Boolean(user?.is_officer);

  // Handlers
  const handleToggleFaq = async () => {
    if (!ticket) return;
    setTogglingFaq(true);
    try {
      await apiClient.post(`/tickets/${ticket.id}/toggle-faq`);
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      alert(getErrorMessage(err, 'FAQ 상태 변경 실패'));
    } finally {
      setTogglingFaq(false);
    }
  };

  const handleResolveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket || !resolutionNote.trim()) return;
    setSubmittingResolve(true);
    setResolveError('');
    try {
      await apiClient.post(`/tickets/${ticket.id}/resolve`, {
        resolution_note: resolutionNote.trim(),
        if_match_write_date: ticket.write_date,
      });
      setResolutionNote('');
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setResolveError(getErrorMessage(err, '조치 완료 처리에 실패했습니다.'));
    } finally {
      setSubmittingResolve(false);
    }
  };

  const handleUpdateResolutionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket || !editResolutionNote.trim()) return;
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
      setEditResolutionError(getErrorMessage(err, '조치 내용 수정에 실패했습니다.'));
    } finally {
      setSubmittingEditResolution(false);
    }
  };

  const handleRestartSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    setSubmittingRestart(true);
    setRestartError('');
    try {
      await apiClient.post(`/tickets/${ticket.id}/restart`, {
        reason: restartReason.trim() || undefined,
      });
      setShowRestartForm(false);
      setRestartReason('');
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setRestartError(getErrorMessage(err, '재문의 등록에 실패했습니다.'));
    } finally {
      setSubmittingRestart(false);
    }
  };

  const handlePendingReplySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket || !pendingReplyText.trim()) return;
    setSubmittingPendingReply(true);
    setPendingReplyError('');
    try {
      await apiClient.post(`/tickets/${ticket.id}/restart`, {
        reason: pendingReplyText.trim(),
      });
      setShowPendingReplyForm(false);
      setPendingReplyText('');
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setPendingReplyError(getErrorMessage(err, '답변 회신 등록에 실패했습니다.'));
    } finally {
      setSubmittingPendingReply(false);
    }
  };

  const handleRatingSubmit = async (e: React.FormEvent) => {
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
      setRatingError(getErrorMessage(err, '만족도 평가 제출에 실패했습니다.'));
    } finally {
      setSubmittingRating(false);
    }
  };

  const handleAssignToMe = async () => {
    if (!ticket) return;
    setTransitioningStatus('assign');
    try {
      await apiClient.post(`/tickets/${ticket.id}/assign`);
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      alert(getErrorMessage(err, '배정 처리에 실패했습니다.'));
    } finally {
      setTransitioningStatus(null);
    }
  };

  const handleStartProgress = async () => {
    if (!ticket) return;
    setTransitioningStatus('start-progress');
    try {
      await apiClient.post(`/tickets/${ticket.id}/start-progress`);
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      alert(getErrorMessage(err, '처리 시작 변경에 실패했습니다.'));
    } finally {
      setTransitioningStatus(null);
    }
  };

  const handlePendingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    setSubmittingPending(true);
    setPendingError('');
    try {
      await apiClient.post(`/tickets/${ticket.id}/pending`, {
        reason: pendingReason.trim() || undefined,
      });
      setShowPendingModal(false);
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setPendingError(getErrorMessage(err, '답변 대기 요청 실패'));
    } finally {
      setSubmittingPending(false);
    }
  };

  const handleCloseSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    setSubmittingClose(true);
    setCloseError('');
    try {
      await apiClient.post(`/tickets/${ticket.id}/close`, {
        note: closeNote.trim() || undefined,
      });
      setShowCloseModal(false);
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setCloseError(getErrorMessage(err, '직권 종결 처리 실패'));
    } finally {
      setSubmittingClose(false);
    }
  };

  const handleCancelSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    setSubmittingCancel(true);
    setCancelError('');
    try {
      await apiClient.post(`/tickets/${ticket.id}/cancel`, {
        reason: cancelReason.trim() || undefined,
      });
      setShowCancelModal(false);
      setIsEditingTicket(false);
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setCancelError(getErrorMessage(err, '문의 취소 실패'));
    } finally {
      setSubmittingCancel(false);
    }
  };

  const handleUpdateTicketSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket || !editTitle.trim() || !editContent.trim()) return;
    setSubmittingEditTicket(true);
    setEditTicketError('');
    try {
      await apiClient.post(`/tickets/${ticket.id}/update`, {
        title: editTitle.trim(),
        category: editCategory,
        priority: editPriority,
        content: editContent.trim(),
      });
      setIsEditingTicket(false);
      await fetchDetail(ticket.id);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setEditTicketError(getErrorMessage(err, '문의 수정 실패'));
    } finally {
      setSubmittingEditTicket(false);
    }
  };

  const handleAttachmentDownload = async (att: Attachment) => {
    if (!ticket) return;
    setDownloadingAttachmentId(att.id);
    try {
      const res = await apiClient.get(`/tickets/${ticket.id}/attachments/${att.id}`);
      const base64Data = res.data.datas;
      const mimetype = res.data.mimetype || 'application/octet-stream';
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: mimetype });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = att.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(getErrorMessage(err, '첨부파일 다운로드에 실패했습니다.'));
    } finally {
      setDownloadingAttachmentId(null);
    }
  };

  const handleAttachmentUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!ticket || !e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    if (file.size > 10 * 1024 * 1024) {
      alert('파일 크기는 최대 10MB를 초과할 수 없습니다.');
      return;
    }
    setUploadingAttachment(true);
    const reader = new FileReader();
    reader.onload = async () => {
      try {
        const base64Data = (reader.result as string).split(',')[1] || '';
        await apiClient.post(`/tickets/${ticket.id}/attachments`, {
          name: file.name,
          datas: base64Data,
          mimetype: file.type || 'application/octet-stream',
        });
        await fetchDetail(ticket.id);
      } catch (err: any) {
        alert(getErrorMessage(err, '첨부파일 업로드 실패'));
      } finally {
        setUploadingAttachment(false);
      }
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-100 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {loading ? (
          <div className="p-12 flex flex-col items-center justify-center space-y-3">
            <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
            <p className="text-xs text-slate-500 font-medium">상세 정보를 불러오는 중입니다...</p>
          </div>
        ) : fetchError ? (
          <div className="p-8 text-center space-y-3">
            <p className="text-sm text-rose-600 font-medium">{fetchError}</p>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200"
            >
              닫기
            </button>
          </div>
        ) : ticket ? (
          <>
            <TicketHeader
              ticket={ticket}
              isOfficer={isOfficer}
              isAuthor={isAuthor}
              togglingFaq={togglingFaq}
              onToggleFaq={handleToggleFaq}
              onClose={onClose}
              onOpenCancel={() => {
                setShowCancelModal(true);
                setCancelReason('');
                setCancelError('');
              }}
              isEditingTicket={isEditingTicket}
              onStartEditTicket={() => {
                setEditTitle(ticket.title || '');
                setEditCategory(ticket.category || 'sw');
                setEditPriority(ticket.priority || '1');
                setEditContent(ticket.content || '');
                setIsEditingTicket(true);
              }}
            />

            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              <TicketMainContent
                ticket={ticket}
                isAuthor={isAuthor}
                isEditingTicket={isEditingTicket}
                editTitle={editTitle}
                setEditTitle={setEditTitle}
                editCategory={editCategory}
                setEditCategory={setEditCategory}
                editPriority={editPriority}
                setEditPriority={setEditPriority}
                editContent={editContent}
                setEditContent={setEditContent}
                submittingEditTicket={submittingEditTicket}
                editTicketError={editTicketError}
                onCancelEditTicket={() => setIsEditingTicket(false)}
                onSubmitEditTicket={handleUpdateTicketSubmit}
                showPendingReplyForm={showPendingReplyForm}
                onOpenPendingReply={() => setShowPendingReplyForm(true)}
                onClosePendingReply={() => setShowPendingReplyForm(false)}
                pendingReplyText={pendingReplyText}
                setPendingReplyText={setPendingReplyText}
                submittingPendingReply={submittingPendingReply}
                pendingReplyError={pendingReplyError}
                onSubmitPendingReply={handlePendingReplySubmit}
              />

              <TicketWorkflowBar
                status={ticket.status}
                isOfficer={isOfficer}
                transitioningStatus={transitioningStatus}
                onAssignToMe={handleAssignToMe}
                onStartProgress={handleStartProgress}
                onOpenPending={() => {
                  setShowPendingModal(true);
                  setPendingReason('');
                  setPendingError('');
                }}
                onOpenClose={() => {
                  setShowCloseModal(true);
                  setCloseNote('');
                  setCloseError('');
                }}
              />

              <TicketAttachments
                attachments={ticket.attachments}
                canUpload={(isAuthor || isOfficer) && !['closed', 'canceled'].includes(ticket.status)}
                uploadingAttachment={uploadingAttachment}
                downloadingAttachmentId={downloadingAttachmentId}
                onFileUpload={handleAttachmentUpload}
                onFileDownload={handleAttachmentDownload}
              />

              <TicketTimeline
                timeline={ticket.timeline}
                isOfficer={isOfficer}
                isEditingResolution={isEditingResolution}
                onStartEditResolution={() => {
                  const resolutionItems = ticket.timeline?.filter((t) => t.type === 'resolution') || [];
                  const latestNote =
                    resolutionItems.length > 0
                      ? resolutionItems[resolutionItems.length - 1].content
                      : ticket.resolution_note || '';
                  setEditResolutionNote(formatHtmlContent(latestNote));
                  setIsEditingResolution(true);
                  setEditResolutionError('');
                }}
              />

              <TicketActionForms
                ticket={ticket}
                isOfficer={isOfficer}
                isAuthor={isAuthor}
                isEditingResolution={isEditingResolution}
                editResolutionNote={editResolutionNote}
                setEditResolutionNote={setEditResolutionNote}
                submittingEditResolution={submittingEditResolution}
                editResolutionError={editResolutionError}
                onCancelEditResolution={() => setIsEditingResolution(false)}
                onSubmitEditResolution={handleUpdateResolutionSubmit}
                resolutionNote={resolutionNote}
                setResolutionNote={setResolutionNote}
                submittingResolve={submittingResolve}
                resolveError={resolveError}
                onSubmitResolve={handleResolveSubmit}
                showRestartForm={showRestartForm}
                onOpenRestart={() => {
                  setShowRestartForm(true);
                  setRestartReason('');
                  setRestartError('');
                }}
                onCloseRestart={() => setShowRestartForm(false)}
                restartReason={restartReason}
                setRestartReason={setRestartReason}
                submittingRestart={submittingRestart}
                restartError={restartError}
                onSubmitRestart={handleRestartSubmit}
                ratingScore={ratingScore}
                setRatingScore={setRatingScore}
                ratingComment={ratingComment}
                setRatingComment={setRatingComment}
                submittingRating={submittingRating}
                ratingError={ratingError}
                onSubmitRating={handleRatingSubmit}
                showCancelModal={showCancelModal}
                onCloseCancelModal={() => setShowCancelModal(false)}
                cancelReason={cancelReason}
                setCancelReason={setCancelReason}
                submittingCancel={submittingCancel}
                cancelError={cancelError}
                onSubmitCancel={handleCancelSubmit}
                showCloseModal={showCloseModal}
                onCloseCloseModal={() => setShowCloseModal(false)}
                closeNote={closeNote}
                setCloseNote={setCloseNote}
                submittingClose={submittingClose}
                closeError={closeError}
                onSubmitClose={handleCloseSubmit}
                showPendingModal={showPendingModal}
                onClosePendingModal={() => setShowPendingModal(false)}
                pendingReason={pendingReason}
                setPendingReason={setPendingReason}
                submittingPending={submittingPending}
                pendingError={pendingError}
                onSubmitPending={handlePendingSubmit}
              />

              <TicketOfficerLogs logs={ticket.logs} isOfficer={isOfficer} />
            </div>

            <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex justify-end">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer transition-colors shadow-2xs"
              >
                닫기
              </button>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
};
