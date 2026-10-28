import { useState } from 'react';
import { workflowApi } from '../../../api/workflowApi';
import { getErrorMessage } from '../../../api/client';
import { TicketDetail } from '../types/ticket';
import { formatHtmlContent } from '../../../shared/utils/htmlUtils';

interface UseTicketResolutionProps {
  ticket: TicketDetail | null;
  onSuccess?: () => void;
  reloadTicket: () => void;
}

export function useTicketResolution({ ticket, onSuccess, reloadTicket }: UseTicketResolutionProps) {
  // Resolve
  const [resolutionNote, setResolutionNote] = useState('');
  const [submittingResolve, setSubmittingResolve] = useState(false);
  const [resolveError, setResolveError] = useState('');

  // Edit Resolution
  const [isEditingResolution, setIsEditingResolution] = useState(false);
  const [editResolutionNote, setEditResolutionNote] = useState('');
  const [submittingEditResolution, setSubmittingEditResolution] = useState(false);
  const [editResolutionError, setEditResolutionError] = useState('');

  // Restart Inquiry
  const [showRestartForm, setShowRestartForm] = useState(false);
  const [restartReason, setRestartReason] = useState('');
  const [submittingRestart, setSubmittingRestart] = useState(false);
  const [restartError, setRestartError] = useState('');

  // Rating
  const [ratingScore, setRatingScore] = useState<number>(5);
  const [ratingComment, setRatingComment] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);
  const [ratingError, setRatingError] = useState('');

  // Pending Reply
  const [showPendingReplyForm, setShowPendingReplyForm] = useState(false);
  const [pendingReplyText, setPendingReplyText] = useState('');
  const [submittingPendingReply, setSubmittingPendingReply] = useState(false);
  const [pendingReplyError, setPendingReplyError] = useState('');

  const onSubmitResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    if (!resolutionNote.trim()) {
      setResolveError('조치 완료 내용을 입력해 주세요.');
      return;
    }
    setSubmittingResolve(true);
    setResolveError('');
    try {
      await workflowApi.resolveTicket(ticket.id, {
        resolution_note: resolutionNote,
        expected_write_date: ticket.write_date,
      });
      setResolutionNote('');
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setResolveError(getErrorMessage(err, '조치 완료 처리에 실패했습니다.'));
    } finally {
      setSubmittingResolve(false);
    }
  };

  const onStartEditResolution = () => {
    if (!ticket) return;
    const initialText = ticket.resolution_note || '';
    setEditResolutionNote(formatHtmlContent(initialText));
    setEditResolutionError('');
    setIsEditingResolution(true);
  };

  const onCancelEditResolution = () => {
    setIsEditingResolution(false);
    setEditResolutionError('');
  };

  const onSubmitEditResolution = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    if (!editResolutionNote.trim()) {
      setEditResolutionError('조치 완료 내용을 입력해 주세요.');
      return;
    }
    setSubmittingEditResolution(true);
    setEditResolutionError('');
    try {
      await workflowApi.updateResolution(ticket.id, editResolutionNote);
      setIsEditingResolution(false);
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setEditResolutionError(getErrorMessage(err, '조치 내용 수정에 실패했습니다.'));
    } finally {
      setSubmittingEditResolution(false);
    }
  };

  const onSubmitRestart = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    if (!restartReason.trim()) {
      setRestartError('재문의 내용을 입력해 주세요.');
      return;
    }
    setSubmittingRestart(true);
    setRestartError('');
    try {
      await workflowApi.restartInquiry(ticket.id, restartReason);
      setShowRestartForm(false);
      setRestartReason('');
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setRestartError(getErrorMessage(err, '재문의 등록에 실패했습니다.'));
    } finally {
      setSubmittingRestart(false);
    }
  };

  const onSubmitRating = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    setSubmittingRating(true);
    setRatingError('');
    try {
      await workflowApi.submitRating(ticket.id, ratingScore, ratingComment);
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setRatingError(getErrorMessage(err, '만족도 평가 등록에 실패했습니다.'));
    } finally {
      setSubmittingRating(false);
    }
  };

  const onOpenPendingReply = () => {
    setShowPendingReplyForm(true);
    setPendingReplyText('');
    setPendingReplyError('');
  };

  const onClosePendingReply = () => {
    setShowPendingReplyForm(false);
    setPendingReplyText('');
    setPendingReplyError('');
  };

  const onSubmitPendingReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    if (!pendingReplyText.trim()) {
      setPendingReplyError('답변 내용을 입력해 주세요.');
      return;
    }
    setSubmittingPendingReply(true);
    setPendingReplyError('');
    try {
      await workflowApi.replyPending(ticket.id, pendingReplyText);
      setShowPendingReplyForm(false);
      setPendingReplyText('');
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setPendingReplyError(getErrorMessage(err, '답변 등록에 실패했습니다.'));
    } finally {
      setSubmittingPendingReply(false);
    }
  };

  return {
    resolutionNote,
    setResolutionNote,
    submittingResolve,
    resolveError,
    onSubmitResolve,
    isEditingResolution,
    editResolutionNote,
    setEditResolutionNote,
    submittingEditResolution,
    editResolutionError,
    onStartEditResolution,
    onCancelEditResolution,
    onSubmitEditResolution,
    showRestartForm,
    setShowRestartForm,
    restartReason,
    setRestartReason,
    submittingRestart,
    restartError,
    onSubmitRestart,
    ratingScore,
    setRatingScore,
    ratingComment,
    setRatingComment,
    submittingRating,
    ratingError,
    onSubmitRating,
    showPendingReplyForm,
    pendingReplyText,
    setPendingReplyText,
    submittingPendingReply,
    pendingReplyError,
    onOpenPendingReply,
    onClosePendingReply,
    onSubmitPendingReply,
  };
}
