import React from 'react';
import {
  User,
  Tag,
  ShieldCheck,
  Calendar,
  Clock,
  AlertTriangle,
  PauseCircle,
  MessageSquare,
  Edit3,
  Ban,
} from 'lucide-react';
import { TicketDetail } from '../../types/ticket';
import { categoryMap } from '../../../../shared/types/common';
import { InquiryEditForm } from './actions/InquiryEditForm';
import { CancelConfirmForm } from './actions/CancelConfirmForm';
import { PendingReplyForm } from './actions/PendingReplyForm';

interface TicketMainContentProps {
  ticket: TicketDetail;
  isAuthor: boolean;
  isOfficer: boolean;
  isEditingTicket: boolean;
  onStartEditTicket: () => void;
  editTitle: string;
  setEditTitle: (val: string) => void;
  editCategory: string;
  setEditCategory: (val: string) => void;
  editPriority: string;
  setEditPriority: (val: string) => void;
  editContent: string;
  setEditContent: (val: string) => void;
  submittingEditTicket: boolean;
  editTicketError: string;
  onCancelEditTicket: () => void;
  onSubmitEditTicket: (e: React.FormEvent) => void;
  showCancelModal: boolean;
  onOpenCancelModal: () => void;
  onCloseCancelModal: () => void;
  cancelReason: string;
  setCancelReason: (val: string) => void;
  submittingCancel: boolean;
  cancelError: string;
  onSubmitCancel: (e: React.FormEvent) => void;
  showPendingReplyForm: boolean;
  onOpenPendingReply: () => void;
  onClosePendingReply: () => void;
  pendingReplyText: string;
  setPendingReplyText: (val: string) => void;
  submittingPendingReply: boolean;
  pendingReplyError: string;
  onSubmitPendingReply: (e: React.FormEvent) => void;
}

export const TicketMainContent: React.FC<TicketMainContentProps> = ({
  ticket,
  isAuthor,
  isOfficer,
  isEditingTicket,
  onStartEditTicket,
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
  onCancelEditTicket,
  onSubmitEditTicket,
  showCancelModal,
  onOpenCancelModal,
  onCloseCancelModal,
  cancelReason,
  setCancelReason,
  submittingCancel,
  cancelError,
  onSubmitCancel,
  showPendingReplyForm,
  onOpenPendingReply,
  onClosePendingReply,
  pendingReplyText,
  setPendingReplyText,
  submittingPendingReply,
  pendingReplyError,
  onSubmitPendingReply,
}) => {
  return (
    <div>
      {/* Title & Action Buttons */}
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-xl font-bold text-slate-900 tracking-tight leading-snug">
          {ticket.title}
        </h2>
        <div className="flex items-center space-x-2 shrink-0">
          {isAuthor && ticket.status === 'submitted' && !isEditingTicket && (
            <button
              type="button"
              onClick={onStartEditTicket}
              className="flex items-center text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 px-2.5 py-1.5 rounded-lg transition-all cursor-pointer shadow-xs"
            >
              <Edit3 className="w-3.5 h-3.5 mr-1" />
              문의 수정
            </button>
          )}
          {!['closed', 'canceled'].includes(ticket.status) && (isAuthor || isOfficer) && (
            <button
              type="button"
              onClick={onOpenCancelModal}
              className="flex items-center text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 px-2.5 py-1.5 rounded-lg transition-all cursor-pointer shadow-xs"
            >
              <Ban className="w-3.5 h-3.5 mr-1" />
              문의 취소
            </button>
          )}
        </div>
      </div>

      {/* Cancel Confirmation Prompt */}
      {showCancelModal && (
        <CancelConfirmForm
          cancelReason={cancelReason}
          setCancelReason={setCancelReason}
          submitting={submittingCancel}
          error={cancelError}
          onCancel={onCloseCancelModal}
          onSubmit={onSubmitCancel}
        />
      )}

      {/* Inline Edit Form for Submitted Ticket */}
      {isEditingTicket && (
        <InquiryEditForm
          editTitle={editTitle}
          setEditTitle={setEditTitle}
          editCategory={editCategory}
          setEditCategory={setEditCategory}
          editPriority={editPriority}
          setEditPriority={setEditPriority}
          editContent={editContent}
          setEditContent={setEditContent}
          submitting={submittingEditTicket}
          error={editTicketError}
          onCancel={onCancelEditTicket}
          onSubmit={onSubmitEditTicket}
        />
      )}

      {/* Metadata 4-column Grid */}
      <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-100 text-xs">
        <div>
          <span className="text-slate-400 flex items-center mb-1">
            <User className="w-3.5 h-3.5 mr-1" /> 작성자
          </span>
          <span className="font-semibold text-slate-800">
            {ticket.author_name || '사원'}
          </span>
        </div>
        <div>
          <span className="text-slate-400 flex items-center mb-1">
            <Tag className="w-3.5 h-3.5 mr-1" /> 카테고리
          </span>
          <span className="font-semibold text-slate-800">
            {categoryMap[ticket.category] || ticket.category}
          </span>
        </div>
        <div>
          <span className="text-slate-400 flex items-center mb-1">
            <ShieldCheck className="w-3.5 h-3.5 mr-1" /> 담당자
          </span>
          <span className="font-semibold text-slate-800">
            {ticket.assignee_name || '배정 대기'}
          </span>
        </div>
        <div>
          <span className="text-slate-400 flex items-center mb-1">
            <Calendar className="w-3.5 h-3.5 mr-1" /> 접수일시
          </span>
          <span className="font-semibold text-slate-800">
            {ticket.create_date ? ticket.create_date.substring(0, 16).replace('T', ' ') : '-'}
          </span>
        </div>
      </div>

      {/* SLA Warning Banner */}
      {ticket.deadline && (
        <div
          className={`mt-3 flex items-center justify-between px-3.5 py-2 rounded-xl text-xs border ${
            ticket.is_overdue
              ? 'bg-rose-50 border-rose-200 text-rose-700'
              : 'bg-amber-50 border-amber-200 text-amber-800'
          }`}
        >
          <div className="flex items-center font-medium">
            {ticket.is_overdue ? (
              <AlertTriangle className="w-4 h-4 mr-1.5 text-rose-600" />
            ) : (
              <Clock className="w-4 h-4 mr-1.5 text-amber-600" />
            )}
            <span>SLA 조치 기한: {ticket.deadline.substring(0, 16).replace('T', ' ')}</span>
          </div>
          {ticket.is_overdue && (
            <span className="font-bold text-rose-700 bg-rose-100 px-2 py-0.5 rounded">
              기한 초과
            </span>
          )}
        </div>
      )}

      {/* Pending Notice Banner */}
      {ticket.status === 'pending' && (
        <div className="mt-3 p-4 bg-purple-50/90 border border-purple-200 rounded-xl flex items-start space-x-3 shadow-xs animate-in fade-in">
          <PauseCircle className="w-5 h-5 text-purple-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-purple-900">IT 담당자 답변 대기 요청 안내</h4>
              <span className="text-[10px] font-semibold bg-purple-200/80 text-purple-800 px-2 py-0.5 rounded-full">
                답변 대기 중
              </span>
            </div>
            <p className="text-xs text-purple-800 mt-1.5 whitespace-pre-wrap leading-relaxed">
              {ticket.pending_reason || '추가 확인 사항에 대해 요청 직원의 확인 및 답변을 기다리고 있습니다.'}
            </p>
            {isAuthor && (
              <div className="mt-3 pt-3 border-t border-purple-200/80">
                {!showPendingReplyForm ? (
                  <button
                    type="button"
                    onClick={onOpenPendingReply}
                    className="inline-flex items-center text-xs font-semibold text-purple-700 bg-white border border-purple-300 hover:bg-purple-100/50 px-3 py-1.5 rounded-lg shadow-xs transition-all cursor-pointer"
                  >
                    <MessageSquare className="w-3.5 h-3.5 mr-1.5" />
                    추가 답변 / 정보 입력하기
                  </button>
                ) : (
                  <PendingReplyForm
                    pendingReplyText={pendingReplyText}
                    setPendingReplyText={setPendingReplyText}
                    submitting={submittingPendingReply}
                    error={pendingReplyError}
                    onCancel={onClosePendingReply}
                    onSubmit={onSubmitPendingReply}
                  />
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
