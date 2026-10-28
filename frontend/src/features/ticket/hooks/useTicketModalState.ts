import { useAuthStore } from '../../../stores/authStore';
import { useTicketDetail } from './useTicketDetail';
import { useTicketInquiryEdit } from './useTicketInquiryEdit';
import { useTicketWorkflow } from './useTicketWorkflow';
import { useTicketResolution } from './useTicketResolution';
import { useTicketAttachments } from './useTicketAttachments';

export function useTicketModalState(
  ticketId: number | null,
  isOpen: boolean,
  onSuccess?: () => void
) {
  const { user } = useAuthStore();

  // 1. Ticket Detail & Permissions Sub-Hook
  const detail = useTicketDetail(ticketId, isOpen);
  const { ticket, reloadTicket } = detail;

  // 2. Inquiry Edit & Cancel Sub-Hook
  const inquiryEdit = useTicketInquiryEdit({
    ticket,
    onSuccess,
    reloadTicket,
  });

  // 3. Workflow Transition Sub-Hook (Assign, Progress, Pending, Close)
  const workflow = useTicketWorkflow({
    ticket,
    user,
    isOpen,
    onSuccess,
    reloadTicket,
  });

  // 4. Resolution, Rating & Pending Reply Sub-Hook
  const resolution = useTicketResolution({
    ticket,
    onSuccess,
    reloadTicket,
  });

  // 5. Attachments Sub-Hook
  const attachments = useTicketAttachments({
    ticket,
    onSuccess,
    reloadTicket,
  });

  return {
    // Detail & Permissions
    ticket: detail.ticket,
    loading: detail.loading,
    fetchError: detail.fetchError,
    faqLoading: detail.faqLoading,
    togglingFaq: detail.faqLoading,
    handleToggleFaq: detail.handleToggleFaq,
    isAuthor: detail.permissions.isAuthor,
    isOfficer: detail.permissions.isOfficer,
    isAssignee: detail.permissions.isAssignee,
    isAdmin: detail.permissions.isAdmin,
    isOwnerOrAdmin: detail.permissions.isOwnerOrAdmin,
    permissions: detail.permissions,

    // Inquiry Edit
    isEditingTicket: inquiryEdit.isEditingTicket,
    setIsEditingTicket: (editing?: boolean) => {
      if (editing === false) inquiryEdit.onCancelEditTicket();
      else inquiryEdit.onStartEditTicket();
    },
    editTitle: inquiryEdit.editTitle,
    setEditTitle: inquiryEdit.setEditTitle,
    editCategory: inquiryEdit.editCategory,
    setEditCategory: inquiryEdit.setEditCategory,
    editPriority: inquiryEdit.editPriority,
    setEditPriority: inquiryEdit.setEditPriority,
    editContent: inquiryEdit.editContent,
    setEditContent: inquiryEdit.setEditContent,
    submittingEditTicket: inquiryEdit.submittingEditTicket,
    editTicketError: inquiryEdit.editTicketError,
    setEditTicketError: (_val?: string) => {},
    onStartEditTicket: inquiryEdit.onStartEditTicket,
    onCancelEditTicket: inquiryEdit.onCancelEditTicket,
    onSubmitEditTicket: inquiryEdit.onSubmitEditTicket,
    handleUpdateTicketSubmit: inquiryEdit.onSubmitEditTicket,

    // Cancel
    showCancelModal: inquiryEdit.showCancelModal,
    setShowCancelModal: (show: boolean) => {
      if (show) inquiryEdit.onOpenCancelModal();
      else inquiryEdit.onCloseCancelModal();
    },
    cancelReason: inquiryEdit.cancelReason,
    setCancelReason: inquiryEdit.setCancelReason,
    submittingCancel: inquiryEdit.submittingCancel,
    cancelError: inquiryEdit.cancelError,
    setCancelError: (_val?: string) => {},
    onOpenCancelModal: inquiryEdit.onOpenCancelModal,
    onCloseCancelModal: inquiryEdit.onCloseCancelModal,
    onSubmitCancel: inquiryEdit.onSubmitCancel,
    handleCancelSubmit: inquiryEdit.onSubmitCancel,

    // Workflow Actions
    transitioningStatus: workflow.transitioningStatus,
    officers: workflow.officers,
    showDesignateModal: workflow.showDesignateModal,
    setShowDesignateModal: workflow.setShowDesignateModal,
    selectedAssignOfficerId: workflow.selectedAssignOfficerId,
    setSelectedAssignOfficerId: workflow.setSelectedAssignOfficerId,
    assignReason: workflow.assignReason,
    setAssignReason: workflow.setAssignReason,
    submittingDesignate: workflow.submittingDesignate,
    designateError: workflow.designateError,
    setDesignateError: workflow.setDesignateError,
    onToggleDesignate: workflow.onToggleDesignate,
    onSubmitDesignate: workflow.onSubmitDesignate,
    handleAssignToOfficer: workflow.onSubmitDesignate,
    onAssignToMe: workflow.onAssignToMe,
    handleAssignToMe: workflow.onAssignToMe,
    onStartProgress: workflow.onStartProgress,
    handleStartProgress: workflow.onStartProgress,

    // Pending
    showPendingModal: workflow.showPendingModal,
    setShowPendingModal: workflow.setShowPendingModal,
    pendingReason: workflow.pendingReason,
    setPendingReason: workflow.setPendingReason,
    submittingPending: workflow.submittingPending,
    pendingError: workflow.pendingError,
    setPendingError: workflow.setPendingError,
    onTogglePending: workflow.onTogglePending,
    onClosePendingModal: workflow.onClosePendingModal,
    onSubmitPending: workflow.onSubmitPending,
    handlePendingSubmit: workflow.onSubmitPending,

    // Pending Reply
    showPendingReplyForm: resolution.showPendingReplyForm,
    setShowPendingReplyForm: (show: boolean) => {
      if (show) resolution.onOpenPendingReply();
      else resolution.onClosePendingReply();
    },
    pendingReplyText: resolution.pendingReplyText,
    setPendingReplyText: resolution.setPendingReplyText,
    submittingPendingReply: resolution.submittingPendingReply,
    pendingReplyError: resolution.pendingReplyError,
    setPendingReplyError: (_val?: string) => {},
    onOpenPendingReply: resolution.onOpenPendingReply,
    onClosePendingReply: resolution.onClosePendingReply,
    onSubmitPendingReply: resolution.onSubmitPendingReply,
    handlePendingReplySubmit: resolution.onSubmitPendingReply,

    // Resolution
    resolutionNote: resolution.resolutionNote,
    setResolutionNote: resolution.setResolutionNote,
    submittingResolve: resolution.submittingResolve,
    resolveError: resolution.resolveError,
    onSubmitResolve: resolution.onSubmitResolve,
    handleResolveSubmit: resolution.onSubmitResolve,
    isEditingResolution: resolution.isEditingResolution,
    setIsEditingResolution: (editing?: boolean) => {
      if (editing === false) resolution.onCancelEditResolution();
      else resolution.onStartEditResolution();
    },
    editResolutionNote: resolution.editResolutionNote,
    setEditResolutionNote: resolution.setEditResolutionNote,
    submittingEditResolution: resolution.submittingEditResolution,
    editResolutionError: resolution.editResolutionError,
    setEditResolutionError: (_val?: string) => {},
    onStartEditResolution: resolution.onStartEditResolution,
    onCancelEditResolution: resolution.onCancelEditResolution,
    onSubmitEditResolution: resolution.onSubmitEditResolution,
    handleUpdateResolutionSubmit: resolution.onSubmitEditResolution,

    // Restart Inquiry
    showRestartForm: resolution.showRestartForm,
    setShowRestartForm: resolution.setShowRestartForm,
    restartReason: resolution.restartReason,
    setRestartReason: resolution.setRestartReason,
    submittingRestart: resolution.submittingRestart,
    restartError: resolution.restartError,
    setRestartError: (_val?: string) => {},
    onSubmitRestart: resolution.onSubmitRestart,
    handleRestartSubmit: resolution.onSubmitRestart,

    // Rating
    ratingScore: resolution.ratingScore,
    setRatingScore: resolution.setRatingScore,
    ratingComment: resolution.ratingComment,
    setRatingComment: resolution.setRatingComment,
    submittingRating: resolution.submittingRating,
    ratingError: resolution.ratingError,
    onSubmitRating: resolution.onSubmitRating,
    handleRatingSubmit: resolution.onSubmitRating,

    // Close
    showCloseModal: workflow.showCloseModal,
    setShowCloseModal: workflow.setShowCloseModal,
    closeNote: workflow.closeNote,
    setCloseNote: workflow.setCloseNote,
    submittingClose: workflow.submittingClose,
    closeError: workflow.closeError,
    setCloseError: workflow.setCloseError,
    onOpenClose: workflow.onOpenClose,
    onCloseCloseModal: workflow.onCloseCloseModal,
    onSubmitClose: workflow.onSubmitClose,
    handleCloseSubmit: workflow.onSubmitClose,

    // Attachments
    uploadingAttachment: attachments.uploadingAttachment,
    downloadingAttachmentId: attachments.downloadingAttachmentId,
    handleUploadAttachment: attachments.handleUploadAttachment,
    handleAttachmentUpload: (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        attachments.handleUploadAttachment(file);
      }
    },
    handleDownloadAttachment: attachments.handleDownloadAttachment,
    handleAttachmentDownload: attachments.handleDownloadAttachment,
  };
}
