import React from 'react';
import { TicketDetail, Attachment } from './ticket';

export interface InquiryEditSectionState {
  isEditingInquiry: boolean;
  editCategory: string;
  editContent: string;
  setEditCategory: (cat: string) => void;
  setEditContent: (val: string) => void;
  handleStartInquiryEdit: () => void;
  handleCancelInquiryEdit: () => void;
  handleSaveInquiryEdit: () => Promise<void>;
}

export interface CancelSectionState {
  isCancelConfirmOpen: boolean;
  cancelReason: string;
  setIsCancelConfirmOpen: (open: boolean) => void;
  setCancelReason: (reason: string) => void;
  handleOpenCancelConfirm: () => void;
  handleCancelTicket: () => Promise<void>;
}

export interface PendingReplySectionState {
  isReplyingToPending: boolean;
  pendingReplyContent: string;
  setIsReplyingToPending: (open: boolean) => void;
  setPendingReplyContent: (val: string) => void;
  handleStartPendingReply: () => void;
  handleCancelPendingReply: () => void;
  handleSavePendingReply: () => Promise<void>;
}

export interface WorkflowSectionState {
  isAssigningOfficer: boolean;
  targetOfficerId: number | null;
  officersList: Array<{ id: number; name: string; login: string }>;
  isPendingModalOpen: boolean;
  pendingReason: string;
  isForceCloseModalOpen: boolean;
  forceCloseReason: string;
  setIsAssigningOfficer: (open: boolean) => void;
  setTargetOfficerId: (id: number | null) => void;
  setIsPendingModalOpen: (open: boolean) => void;
  setPendingReason: (val: string) => void;
  setIsForceCloseModalOpen: (open: boolean) => void;
  setForceCloseReason: (val: string) => void;
  handleAssignSelf: () => Promise<void>;
  handleConfirmAssignOfficer: () => Promise<void>;
  handleStartProgress: () => Promise<void>;
  handleConfirmPending: () => Promise<void>;
  handleConfirmForceClose: () => Promise<void>;
}

export interface ResolutionSectionState {
  resolutionContent: string;
  setResolutionContent: (val: string) => void;
  isResolutionSubmitting: boolean;
  handleSubmitResolution: (e: React.FormEvent) => Promise<void>;
  isEditingResolution: boolean;
  editResolutionContent: string;
  setEditResolutionContent: (val: string) => void;
  handleStartEditResolution: () => void;
  handleCancelEditResolution: () => void;
  handleSaveEditResolution: () => Promise<void>;
  isReInquiryOpen: boolean;
  reInquiryContent: string;
  setReInquiryContent: (val: string) => void;
  setIsReInquiryOpen: (open: boolean) => void;
  handleSubmitReInquiry: (e: React.FormEvent) => Promise<void>;
  rating: number;
  ratingComment: string;
  setRating: (rating: number) => void;
  setRatingComment: (comment: string) => void;
  isRatingSubmitting: boolean;
  handleSubmitRating: (e: React.FormEvent) => Promise<void>;
}

export interface AttachmentSectionState {
  uploadingAttachment: boolean;
  downloadingAttachmentId: number | null;
  attachmentError: string | null;
  fileInputRef: React.RefObject<HTMLInputElement>;
  handleAttachmentUpload: (e: React.ChangeEvent<HTMLInputElement>) => Promise<void>;
  handleAttachmentDownload: (att: Attachment) => Promise<void>;
}

export interface TicketPermissions {
  isAuthor: boolean;
  isOfficer: boolean;
  isAssignee: boolean;
  isAdmin: boolean;
  isOwnerOrAdmin: boolean;
}

export interface TicketModalStateFacade {
  ticket: TicketDetail | null;
  loading: boolean;
  error: string | null;
  faqLoading: boolean;
  handleToggleFaq: () => Promise<void>;
  permissions: TicketPermissions;
  inquiryEdit: InquiryEditSectionState;
  cancel: CancelSectionState;
  pendingReply: PendingReplySectionState;
  workflow: WorkflowSectionState;
  resolution: ResolutionSectionState;
  attachments: AttachmentSectionState;
}
