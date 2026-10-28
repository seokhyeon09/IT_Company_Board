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
  const s = useTicketModalState(ticketId, isOpen, onSuccess);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-100 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {s.loading ? (
          <div className="p-12 flex flex-col items-center justify-center space-y-3">
            <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
            <p className="text-xs text-slate-500 font-medium">상세 정보를 불러오는 중입니다...</p>
          </div>
        ) : s.fetchError ? (
          <div className="p-8 text-center space-y-3">
            <p className="text-sm text-rose-600 font-medium">{s.fetchError}</p>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200"
            >
              닫기
            </button>
          </div>
        ) : s.ticket ? (
          <>
            <TicketHeader
              ticket={s.ticket}
              isOfficer={s.isOfficer}
              isAuthor={s.isAuthor}
              togglingFaq={s.togglingFaq}
              onToggleFaq={s.handleToggleFaq}
              onClose={onClose}
              onOpenCancel={() => {
                s.setShowCancelModal(true);
                s.setCancelReason('');
              }}
              isEditingTicket={s.isEditingTicket}
              onStartEditTicket={() => {
                s.setEditTitle(s.ticket?.title || '');
                s.setEditCategory(s.ticket?.category || 'sw');
                s.setEditPriority(s.ticket?.priority || '1');
                s.setEditContent(s.ticket?.content || '');
                s.setIsEditingTicket(true);
              }}
            />

            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              <TicketMainContent
                ticket={s.ticket}
                isAuthor={s.isAuthor}
                isEditingTicket={s.isEditingTicket}
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
                showPendingReplyForm={s.showPendingReplyForm}
                onOpenPendingReply={() => s.setShowPendingReplyForm(true)}
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
                onOpenPending={() => {
                  s.setShowPendingModal(true);
                  s.setPendingReason('');
                }}
                onOpenClose={() => {
                  s.setShowCloseModal(true);
                  s.setCloseNote('');
                }}
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
                }}
              />

              <TicketActionForms
                ticket={s.ticket}
                isOfficer={s.isOfficer}
                isAuthor={s.isAuthor}
                isEditingResolution={s.isEditingResolution}
                editResolutionNote={s.editResolutionNote}
                setEditResolutionNote={s.setEditResolutionNote}
                submittingEditResolution={s.submittingEditResolution}
                editResolutionError={s.editResolutionError}
                onCancelEditResolution={() => s.setIsEditingResolution(false)}
                onSubmitEditResolution={s.handleUpdateResolutionSubmit}
                resolutionNote={s.resolutionNote}
                setResolutionNote={s.setResolutionNote}
                submittingResolve={s.submittingResolve}
                resolveError={s.resolveError}
                onSubmitResolve={s.handleResolveSubmit}
                showRestartForm={s.showRestartForm}
                onOpenRestart={() => {
                  s.setShowRestartForm(true);
                  s.setRestartReason('');
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
                showCancelModal={s.showCancelModal}
                onCloseCancelModal={() => s.setShowCancelModal(false)}
                cancelReason={s.cancelReason}
                setCancelReason={s.setCancelReason}
                submittingCancel={s.submittingCancel}
                cancelError={s.cancelError}
                onSubmitCancel={s.handleCancelSubmit}
                showCloseModal={s.showCloseModal}
                onCloseCloseModal={() => s.setShowCloseModal(false)}
                closeNote={s.closeNote}
                setCloseNote={s.setCloseNote}
                submittingClose={s.submittingClose}
                closeError={s.closeError}
                onSubmitClose={s.handleCloseSubmit}
                showPendingModal={s.showPendingModal}
                onClosePendingModal={() => s.setShowPendingModal(false)}
                pendingReason={s.pendingReason}
                setPendingReason={s.setPendingReason}
                submittingPending={s.submittingPending}
                pendingError={s.pendingError}
                onSubmitPending={s.handlePendingSubmit}
              />

              <TicketOfficerLogs logs={s.ticket.logs} isOfficer={s.isOfficer} />
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
