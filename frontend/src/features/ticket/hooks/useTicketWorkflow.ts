import { useState, useEffect } from 'react';
import { workflowApi } from '../../../api/workflowApi';
import { ticketApi } from '../../../api/ticketApi';
import { getErrorMessage } from '../../../api/client';
import { TicketDetail, OfficerSimpleItem } from '../types/ticket';
import { UserProfile } from '../../../stores/authStore';

interface UseTicketWorkflowProps {
  ticket: TicketDetail | null;
  user: UserProfile | null;
  isOpen: boolean;
  onSuccess?: () => void;
  reloadTicket: () => void;
}

export function useTicketWorkflow({
  ticket,
  user,
  isOpen,
  onSuccess,
  reloadTicket,
}: UseTicketWorkflowProps) {
  const [transitioningStatus, setTransitioningStatus] = useState<string | null>(null);

  // Designation / Reassignment
  const [officers, setOfficers] = useState<OfficerSimpleItem[]>([]);
  const [showDesignateModal, setShowDesignateModal] = useState(false);
  const [selectedAssignOfficerId, setSelectedAssignOfficerId] = useState<number | ''>('');
  const [assignReason, setAssignReason] = useState('');
  const [submittingDesignate, setSubmittingDesignate] = useState(false);
  const [designateError, setDesignateError] = useState('');

  // Pending
  const [showPendingModal, setShowPendingModal] = useState(false);
  const [pendingReason, setPendingReason] = useState('');
  const [submittingPending, setSubmittingPending] = useState(false);
  const [pendingError, setPendingError] = useState('');

  // Close
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [closeNote, setCloseNote] = useState('');
  const [submittingClose, setSubmittingClose] = useState(false);
  const [closeError, setCloseError] = useState('');

  useEffect(() => {
    if (isOpen && (user?.is_officer || user?.is_manager || user?.is_admin)) {
      ticketApi
        .getOfficers()
        .then((res: any) => {
          const list = Array.isArray(res) ? res : res?.officers || res?.data || [];
          setOfficers(list);
        })
        .catch(() => setOfficers([]));
    }
  }, [isOpen, user?.is_officer, user?.is_manager, user?.is_admin]);

  const onAssignToMe = async () => {
    if (!ticket) return;
    setTransitioningStatus('assign');
    try {
      await workflowApi.assignSelf(ticket.id);
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      alert(getErrorMessage(err, '담당자 배정에 실패했습니다.'));
    } finally {
      setTransitioningStatus(null);
    }
  };

  const onStartProgress = async () => {
    if (!ticket) return;
    setTransitioningStatus('start-progress');
    try {
      await workflowApi.startProgress(ticket.id);
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      alert(getErrorMessage(err, '처리 시작 처리에 실패했습니다.'));
    } finally {
      setTransitioningStatus(null);
    }
  };

  const onToggleDesignate = () => {
    setShowDesignateModal(!showDesignateModal);
    setSelectedAssignOfficerId('');
    setAssignReason('');
    setDesignateError('');
  };

  const onSubmitDesignate = async () => {
    if (!ticket || !selectedAssignOfficerId) return;
    setSubmittingDesignate(true);
    setDesignateError('');
    try {
      await workflowApi.assignOfficer(
        ticket.id,
        Number(selectedAssignOfficerId),
        assignReason.trim() || undefined
      );
      setShowDesignateModal(false);
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setDesignateError(getErrorMessage(err, '담당자 지정/인계 처리에 실패했습니다.'));
    } finally {
      setSubmittingDesignate(false);
    }
  };

  const onTogglePending = () => {
    setShowPendingModal(!showPendingModal);
    setPendingReason('');
    setPendingError('');
  };

  const onClosePendingModal = () => {
    setShowPendingModal(false);
    setPendingReason('');
    setPendingError('');
  };

  const onSubmitPending = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    if (!pendingReason.trim()) {
      setPendingError('대기 사유를 입력해 주세요.');
      return;
    }
    setSubmittingPending(true);
    setPendingError('');
    try {
      await workflowApi.requestPending(ticket.id, pendingReason);
      setShowPendingModal(false);
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setPendingError(getErrorMessage(err, '답변 대기 상태 전환에 실패했습니다.'));
    } finally {
      setSubmittingPending(false);
    }
  };

  const onOpenClose = () => {
    setShowCloseModal(true);
    setCloseNote('');
    setCloseError('');
  };

  const onCloseCloseModal = () => {
    setShowCloseModal(false);
    setCloseNote('');
    setCloseError('');
  };

  const onSubmitClose = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticket) return;
    setSubmittingClose(true);
    setCloseError('');
    try {
      await workflowApi.closeTicket(ticket.id, closeNote);
      setShowCloseModal(false);
      reloadTicket();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setCloseError(getErrorMessage(err, '종결 처리에 실패했습니다.'));
    } finally {
      setSubmittingClose(false);
    }
  };

  return {
    transitioningStatus,
    officers,
    showDesignateModal,
    setShowDesignateModal,
    selectedAssignOfficerId,
    setSelectedAssignOfficerId,
    assignReason,
    setAssignReason,
    submittingDesignate,
    designateError,
    setDesignateError,
    onToggleDesignate,
    onSubmitDesignate,
    onAssignToMe,
    onStartProgress,
    showPendingModal,
    setShowPendingModal,
    pendingReason,
    setPendingReason,
    submittingPending,
    pendingError,
    setPendingError,
    onTogglePending,
    onClosePendingModal,
    onSubmitPending,
    showCloseModal,
    setShowCloseModal,
    closeNote,
    setCloseNote,
    submittingClose,
    closeError,
    setCloseError,
    onOpenClose,
    onCloseCloseModal,
    onSubmitClose,
  };
}
