import React from 'react';
import { PauseCircle, Clock } from 'lucide-react';
import { TicketDetail } from '../../types/ticket';
import { ResolutionForm } from './actions/ResolutionForm';
import { RestartInquiryForm } from './actions/RestartInquiryForm';
import { RatingForm } from './actions/RatingForm';

interface TicketActionFormsProps {
  ticket: TicketDetail;
  isOfficer: boolean;
  isAuthor: boolean;

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
}

export const TicketActionForms: React.FC<TicketActionFormsProps> = (props) => {
  const { ticket, isOfficer, isAuthor } = props;
  const isResolved = ticket.status === 'resolved';
  const isClosed = ticket.status === 'closed';
  const isCanceled = ticket.status === 'canceled';
  const canResolve = !isResolved && !isClosed && !isCanceled && isOfficer;

  return (
    <div className="space-y-4">
      {/* 1. Employee Follow-up Inquiry Form & Closed Notice */}
      <RestartInquiryForm
        isAuthor={isAuthor}
        isResolved={isResolved}
        isClosed={isClosed}
        timeline={ticket.timeline}
        showRestartForm={props.showRestartForm}
        onOpenRestart={props.onOpenRestart}
        onCloseRestart={props.onCloseRestart}
        restartReason={props.restartReason}
        setRestartReason={props.setRestartReason}
        submittingRestart={props.submittingRestart}
        restartError={props.restartError}
        onSubmitRestart={props.onSubmitRestart}
      />

      {/* 2. Rating Form & Rating Result */}
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

      {/* 3. IT Officer Resolution Action Form */}
      <ResolutionForm
        canResolve={canResolve}
        resolutionNote={props.resolutionNote}
        setResolutionNote={props.setResolutionNote}
        submittingResolve={props.submittingResolve}
        resolveError={props.resolveError}
        onSubmitResolve={props.onSubmitResolve}
      />

      {/* 4. Regular User In-Progress / Pending Message */}
      {!isResolved && !isClosed && !isOfficer && (
        ticket.status === 'pending' ? (
          <div className="p-3.5 bg-purple-50 border border-purple-200 rounded-xl text-purple-900 text-xs flex items-center">
            <PauseCircle className="w-4 h-4 mr-2 text-purple-600 shrink-0" />
            <span>IT 담당자의 답변 대기 요청이 등록되었습니다. 상단 안내를 확인하시고 추가 답변을 등록해 주세요.</span>
          </div>
        ) : (
          <div className="p-3.5 bg-blue-50 border border-blue-200 rounded-xl text-blue-800 text-xs flex items-center">
            <Clock className="w-4 h-4 mr-2 text-blue-600 shrink-0" />
            <span>현재 IT 지원팀에서 담당자 배정 및 문의 처리를 진행 중입니다.</span>
          </div>
        )
      )}
    </div>
  );
};
