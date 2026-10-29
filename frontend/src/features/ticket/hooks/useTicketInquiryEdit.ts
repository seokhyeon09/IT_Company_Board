import { useState } from 'react';
import { ticketApi } from '../../../api/ticketApi';
import { workflowApi } from '../../../api/workflowApi';
import { getErrorMessage } from '../../../api/client';
import { TicketDetail } from '../types/ticket';
import { formatHtmlContent } from '../../../shared/utils/htmlUtils';

interface UseTicketInquiryEditProps {
  ticket: TicketDetail | null;
  onSuccess?: () => void;
  reloadTicket: () => void;
}

export function useTicketInquiryEdit({ ticket, onSuccess, reloadTicket }: UseTicketInquiryEditProps) {
  // Inquiry Edit State
  const [isEditingTicket, setIsEditingTicket] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editCategory, setEditCategory] = useState('');
  const [editPriority, setEditPriority] = useState('');
  const [editContent, setEditContent] = useState('');
  const [submittingEditTicket, setSubmittingEditTicket] = useState(false);
  const [editTicketError, setEditTicketError] = useState('');

  // Cancel State
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [submittingCancel, setSubmittingCancel] = useState(false);
  const [cancelError, setCancelError] = useState('');

  const onStartEditTicket = () => {
    if (!ticket) return;
    setEditTitle(ticket.title);
    setEditCategory(ticket.category);
    setEditPriority(ticket.priority);
    setEditContent(formatHtmlContent(ticket.content));
    setEditTicketError('');
    setIsEditingTicket(true);
  };

  const onCancelEditTicket = () => {
    setIsEditingTicket(false);
    setEditTicketError('');
  };

  const onSubmitEditTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    if (!editTitle.trim()) {
      setEditTicketError('문의 제목을 입력해 주세요.');
      return;
    }
    if (!editContent.trim()) {
      setEditTicketError('상세 내용을 입력해 주세요.');
      return;
    }

    setSubmittingEditTicket(true);
    setEditTicketError('');
    try {
      await ticketApi.updateTicket(ticket.id, {
        title: editTitle,
        category: editCategory,
        priority: editPriority,
        content: editContent,
      });
      setIsEditingTicket(false);
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setEditTicketError(getErrorMessage(err, '문의 내용 수정에 실패했습니다.'));
    } finally {
      setSubmittingEditTicket(false);
    }
  };

  const onOpenCancelModal = () => {
    setShowCancelModal(true);
    setCancelReason('');
    setCancelError('');
  };

  const onCloseCancelModal = () => {
    setShowCancelModal(false);
    setCancelReason('');
    setCancelError('');
  };

  const onSubmitCancel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;

    setSubmittingCancel(true);
    setCancelError('');
    try {
      await workflowApi.cancelTicket(ticket.id, cancelReason);
      setShowCancelModal(false);
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setCancelError(getErrorMessage(err, '문의 취소에 실패했습니다.'));
    } finally {
      setSubmittingCancel(false);
    }
  };

  return {
    isEditingTicket,
    editTitle,
    setEditTitle,
    editCategory,
    setEditCategory,
    editPriority,
    setEditPriority,
    editContent,
    setEditContent,
    submittingEditTicket,
    editTicketError,
    onStartEditTicket,
    onCancelEditTicket,
    onSubmitEditTicket,
    showCancelModal,
    cancelReason,
    setCancelReason,
    submittingCancel,
    cancelError,
    onOpenCancelModal,
    onCloseCancelModal,
    onSubmitCancel,
  };
}
