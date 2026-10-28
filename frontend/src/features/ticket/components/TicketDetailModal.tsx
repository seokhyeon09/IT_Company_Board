import React from 'react';
import { Loader2 } from 'lucide-react';
import { useTicketModalState } from '../hooks/useTicketModalState';
import { formatHtmlContent } from '../../../shared/utils/htmlUtils';

import { TicketHeader } from './modal/TicketHeader';
import { TicketMainContent } from './modal/TicketMainContent';
import { TicketAttachments } from './modal/TicketAttachments';
import { TicketWorkflowBar } from './modal/TicketWorkflowBar';
import { TicketTimeline } from './modal/TicketTimeline';
import { TicketActionForms } from './modal/TicketActionForms';
import { TicketOfficerLogs } from './modal/TicketOfficerLogs';
import { TicketRelatedAndEmails } from './modal/TicketRelatedAndEmails';

export interface TicketDetailModalProps {
  isOpen: boolean;
  ticketId: number | null;
  onClose: () => void;
  onSuccess?: () => void;
  onSelectTicket?: (ticketId: number) => void;
}

export const TicketDetailModal: React.FC<TicketDetailModalProps> = ({
  isOpen,
  ticketId,
  onClose,
  onSuccess,
  onSelectTicket,
}) => {
  const s = useTicketModalState(ticketId, isOpen, onSuccess);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col overflow-hidden border border-slate-100">
        {/* Header */}
        <TicketHeader
          ticket={s.ticket}
          isOfficer={s.isOfficer}
          togglingFaq={s.togglingFaq}
          onToggleFaq={s.handleToggleFaq}
          onClose={onClose}
        />

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-sm text-slate-700">
          {s.loading ? (
            <div className="py-20 text-center text-slate-400 flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mb-3" />
              티켓 상세 정보를 불러오는 중입니다...
            </div>
          ) : s.fetchError ? (
            <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-center">
              <p className="font-bold">오류</p>
              <p className="text-xs mt-1">{s.fetchError}</p>
            </div>
          ) : s.ticket ? (
            <>
              <TicketMainContent
                ticket={s.ticket}
                isAuthor={s.isAuthor}
                isOfficer={s.isOfficer}
                isEditingTicket={s.isEditingTicket}
                onStartEditTicket={() => {
                  s.setEditTitle(s.ticket?.title || '');
                  s.setEditCategory(s.ticket?.category || 'sw');
                  s.setEditPriority(s.ticket?.priority || '1');
                  s.setEditContent(s.ticket?.content || '');
                  s.setIsEditingTicket(true);
                  s.setEditTicketError('');
                }}
                editTitle={s.editTitle}
                setEditTitle={s.setEditTitle}
                editCategory={s.editCategory}
                setEditCategory={s.setEditCategory}
                editPriority={s.editPriority}
                setEditPriority={s.setEditPriority}
                editContent={s.editContent}
                setEditContent={s.setEditContent}
                submittingEditTicket={s.submittingEditTicket}
                editTicketError={s.editTicketError}
                onCancelEditTicket={() => s.setIsEditingTicket(false)}
                onSubmitEditTicket={s.handleUpdateTicketSubmit}
                showCancelModal={s.showCancelModal}
                onOpenCancelModal={() => {
                  s.setShowCancelModal(true);
                  s.setCancelReason('');
                  s.setCancelError('');
                }}
                onCloseCancelModal={() => s.setShowCancelModal(false)}
                cancelReason={s.cancelReason}
                setCancelReason={s.setCancelReason}
                submittingCancel={s.submittingCancel}
                cancelError={s.cancelError}
                onSubmitCancel={s.handleCancelSubmit}
                showPendingReplyForm={s.showPendingReplyForm}
                onOpenPendingReply={() => {
                  s.setShowPendingReplyForm(true);
                  s.setPendingReplyText('');
                  s.setPendingReplyError('');
                }}
                onClosePendingReply={() => s.setShowPendingReplyForm(false)}
                pendingReplyText={s.pendingReplyText}
                setPendingReplyText={s.setPendingReplyText}
                submittingPendingReply={s.submittingPendingReply}
                pendingReplyError={s.pendingReplyError}
                onSubmitPendingReply={s.handlePendingReplySubmit}
              />

              <TicketWorkflowBar
                status={s.ticket.status}
                isOfficer={s.isOfficer}
                transitioningStatus={s.transitioningStatus}
                onAssignToMe={s.handleAssignToMe}
                onStartProgress={s.handleStartProgress}
                officers={s.officers}
                showDesignateModal={s.showDesignateModal}
                onToggleDesignate={() => {
                  s.setShowDesignateModal((prev) => !prev);
                  s.setShowPendingModal(false);
                  s.setShowCloseModal(false);
                }}
                selectedAssignOfficerId={s.selectedAssignOfficerId}
                onSelectAssignOfficer={s.setSelectedAssignOfficerId}
                submittingDesignate={s.submittingDesignate}
                designateError={s.designateError}
                onSubmitDesignate={() => s.handleAssignToOfficer()}
                showPendingModal={s.showPendingModal}
                onTogglePending={() => {
                  s.setShowPendingModal((prev) => !prev);
                  s.setPendingReason('');
                  s.setPendingError('');
                  s.setShowCloseModal(false);
                  s.setShowDesignateModal(false);
                }}
                onClosePendingModal={() => s.setShowPendingModal(false)}
                pendingReason={s.pendingReason}
                setPendingReason={s.setPendingReason}
                submittingPending={s.submittingPending}
                pendingError={s.pendingError}
                onSubmitPending={s.handlePendingSubmit}
                showCloseModal={s.showCloseModal}
                onOpenClose={() => {
                  s.setShowCloseModal(true);
                  s.setCloseNote('');
                  s.setCloseError('');
                  s.setShowPendingModal(false);
                  s.setShowDesignateModal(false);
                }}
                onCloseCloseModal={() => s.setShowCloseModal(false)}
                closeNote={s.closeNote}
                setCloseNote={s.setCloseNote}
                submittingClose={s.submittingClose}
                closeError={s.closeError}
                onSubmitClose={s.handleCloseSubmit}
              />

              <TicketAttachments
                attachments={s.ticket.attachments}
                canUpload={(s.isAuthor || s.isOfficer) && !['closed', 'canceled'].includes(s.ticket.status)}
                uploadingAttachment={s.uploadingAttachment}
                downloadingAttachmentId={s.downloadingAttachmentId}
                onFileUpload={s.handleAttachmentUpload}
                onFileDownload={s.handleAttachmentDownload}
              />

              <TicketTimeline
                timeline={s.ticket.timeline}
                fallbackContent={s.ticket.content}
                isOfficer={s.isOfficer}
                isEditingResolution={s.isEditingResolution}
                onStartEditResolution={() => {
                  const resolutionItems = s.ticket?.timeline?.filter((t) => t.type === 'resolution') || [];
                  const latestNote =
                    resolutionItems.length > 0
                      ? resolutionItems[resolutionItems.length - 1].content
                      : s.ticket?.resolution_note || '';
                  s.setEditResolutionNote(formatHtmlContent(latestNote));
                  s.setIsEditingResolution(true);
                  s.setEditResolutionError('');
                }}
                editResolutionNote={s.editResolutionNote}
                setEditResolutionNote={s.setEditResolutionNote}
                submittingEditResolution={s.submittingEditResolution}
                editResolutionError={s.editResolutionError}
                onCancelEditResolution={() => s.setIsEditingResolution(false)}
                onSubmitEditResolution={s.handleUpdateResolutionSubmit}
              />

              <TicketActionForms
                ticket={s.ticket}
                isOfficer={s.isOfficer}
                isAuthor={s.isAuthor}
                resolutionNote={s.resolutionNote}
                setResolutionNote={s.setResolutionNote}
                submittingResolve={s.submittingResolve}
                resolveError={s.resolveError}
                onSubmitResolve={s.handleResolveSubmit}
                showRestartForm={s.showRestartForm}
                onOpenRestart={() => {
                  s.setShowRestartForm(true);
                  s.setRestartReason('');
                  s.setRestartError('');
                }}
                onCloseRestart={() => s.setShowRestartForm(false)}
                restartReason={s.restartReason}
                setRestartReason={s.setRestartReason}
                submittingRestart={s.submittingRestart}
                restartError={s.restartError}
                onSubmitRestart={s.handleRestartSubmit}
                ratingScore={s.ratingScore}
                setRatingScore={s.setRatingScore}
                ratingComment={s.ratingComment}
                setRatingComment={s.setRatingComment}
                submittingRating={s.submittingRating}
                ratingError={s.ratingError}
                onSubmitRating={s.handleRatingSubmit}
              />

              <TicketRelatedAndEmails
                relatedTickets={s.ticket.related_tickets}
                emailNotifications={s.ticket.email_notifications}
                onSelectRelatedTicket={onSelectTicket}
              />

              <TicketOfficerLogs logs={s.ticket.logs} isOfficer={s.isOfficer} />
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-100 flex justify-end">
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
