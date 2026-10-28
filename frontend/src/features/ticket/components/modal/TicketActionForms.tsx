import React from 'react';
import { TicketDetail } from '../../types/ticket';
import { ResolutionForm } from './actions/ResolutionForm';
import { RestartInquiryForm } from './actions/RestartInquiryForm';
import { RatingForm } from './actions/RatingForm';
import { StatusModals } from './actions/StatusModals';

interface TicketActionFormsProps {
  ticket: TicketDetail;
  isOfficer: boolean;
  isAuthor: boolean;

  // Edit resolution
  isEditingResolution: boolean;
  editResolutionNote: string;
  setEditResolutionNote: (val: string) => void;
  submittingEditResolution: boolean;
  editResolutionError: string;
  onCancelEditResolution: () => void;
  onSubmitEditResolution: (e: React.FormEvent) => void;

  // Resolve (new)
  resolutionNote: string;
  setResolutionNote: (val: string) => void;
  submittingResolve: boolean;
  resolveError: string;
  onSubmitResolve: (e: React.FormEvent) => void;

  // Restart inquiry
  showRestartForm: boolean;
  onOpenRestart: () => void;
  onCloseRestart: () => void;
  restartReason: string;
  setRestartReason: (val: string) => void;
  submittingRestart: boolean;
  restartError: string;
  onSubmitRestart: (e: React.FormEvent) => void;

  // Rating
  ratingScore: number;
  setRatingScore: (val: number) => void;
  ratingComment: string;
  setRatingComment: (val: string) => void;
  submittingRating: boolean;
  ratingError: string;
  onSubmitRating: (e: React.FormEvent) => void;

  // Cancel modal
  showCancelModal: boolean;
  onCloseCancelModal: () => void;
  cancelReason: string;
  setCancelReason: (val: string) => void;
  submittingCancel: boolean;
  cancelError: string;
  onSubmitCancel: (e: React.FormEvent) => void;

  // Close modal
  showCloseModal: boolean;
  onCloseCloseModal: () => void;
  closeNote: string;
  setCloseNote: (val: string) => void;
  submittingClose: boolean;
  closeError: string;
  onSubmitClose: (e: React.FormEvent) => void;

  // Pending modal
  showPendingModal: boolean;
  onClosePendingModal: () => void;
  pendingReason: string;
  setPendingReason: (val: string) => void;
  submittingPending: boolean;
  pendingError: string;
  onSubmitPending: (e: React.FormEvent) => void;
}

export const TicketActionForms: React.FC<TicketActionFormsProps> = (props) => {
  const { ticket, isOfficer, isAuthor } = props;
  const isResolved = ticket.status === 'resolved';
  const isClosed = ticket.status === 'closed';
  const canResolve =
    isOfficer && ['submitted', 'assigned', 'in_progress'].includes(ticket.status);

  return (
    <div className="space-y-4">
      {/* 1. Resolution / Edit Form */}
      <ResolutionForm
        canResolve={canResolve}
        isEditingResolution={props.isEditingResolution}
        editResolutionNote={props.editResolutionNote}
        setEditResolutionNote={props.setEditResolutionNote}
        submittingEditResolution={props.submittingEditResolution}
        editResolutionError={props.editResolutionError}
        onCancelEditResolution={props.onCancelEditResolution}
        onSubmitEditResolution={props.onSubmitEditResolution}
        resolutionNote={props.resolutionNote}
        setResolutionNote={props.setResolutionNote}
        submittingResolve={props.submittingResolve}
        resolveError={props.resolveError}
        onSubmitResolve={props.onSubmitResolve}
      />

      {/* 2. Employee Follow-up Inquiry Form */}
      <RestartInquiryForm
        isAuthor={isAuthor}
        isResolved={isResolved}
        isClosed={isClosed}
        showRestartForm={props.showRestartForm}
        onOpenRestart={props.onOpenRestart}
        onCloseRestart={props.onCloseRestart}
        restartReason={props.restartReason}
        setRestartReason={props.setRestartReason}
        submittingRestart={props.submittingRestart}
        restartError={props.restartError}
        onSubmitRestart={props.onSubmitRestart}
      />

      {/* 3. Rating Form */}
      <RatingForm
        isResolved={isResolved}
        isAuthor={isAuthor}
        rating={ticket.rating}
        ratingComment={ticket.rating_comment}
        ratingScore={props.ratingScore}
        setRatingScore={props.setRatingScore}
        ratingCommentInput={props.ratingComment}
        setRatingCommentInput={props.setRatingComment}
        submittingRating={props.submittingRating}
        ratingError={props.ratingError}
        onSubmitRating={props.onSubmitRating}
      />

      {/* 4. Action Confirmation Modals */}
      <StatusModals
        showCancelModal={props.showCancelModal}
        onCloseCancelModal={props.onCloseCancelModal}
        cancelReason={props.cancelReason}
        setCancelReason={props.setCancelReason}
        submittingCancel={props.submittingCancel}
        cancelError={props.cancelError}
        onSubmitCancel={props.onSubmitCancel}
        showCloseModal={props.showCloseModal}
        onCloseCloseModal={props.onCloseCloseModal}
        closeNote={props.closeNote}
        setCloseNote={props.setCloseNote}
        submittingClose={props.submittingClose}
        closeError={props.closeError}
        onSubmitClose={props.onSubmitClose}
        showPendingModal={props.showPendingModal}
        onClosePendingModal={props.onClosePendingModal}
        pendingReason={props.pendingReason}
        setPendingReason={props.setPendingReason}
        submittingPending={props.submittingPending}
        pendingError={props.pendingError}
        onSubmitPending={props.onSubmitPending}
      />
    </div>
  );
};
