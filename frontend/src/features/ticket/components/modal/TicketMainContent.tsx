import React from 'react';
import {
  User,
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  MessageSquare,
  Loader2,
} from 'lucide-react';
import { TicketDetail } from '../../types/ticket';
import { formatHtmlContent } from '../../../../shared/utils/htmlUtils';

interface TicketMainContentProps {
  ticket: TicketDetail;
  isAuthor: boolean;
  isEditingTicket: boolean;
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
  onCancelEditTicket,
  onSubmitEditTicket,
  showPendingReplyForm,
  onOpenPendingReply,
  onClosePendingReply,
  pendingReplyText,
  setPendingReplyText,
  submittingPendingReply,
  pendingReplyError,
  onSubmitPendingReply,
}) => {
  const isOverdue = ticket.is_overdue;

  // SLA 계산
  let slaBadge = null;
  if (ticket.deadline && !['resolved', 'closed', 'canceled'].includes(ticket.status)) {
    const now = new Date().getTime();
    const deadlineTime = new Date(ticket.deadline).getTime();
    const diffHours = Math.round((deadlineTime - now) / (1000 * 60 * 60));

    if (diffHours < 0) {
      slaBadge = (
        <span className="flex items-center text-xs font-bold text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded-full">
          <AlertTriangle className="w-3 h-3 mr-1" />
          SLA {Math.abs(diffHours)}시간 초과
        </span>
      );
    } else {
      slaBadge = (
        <span className="flex items-center text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
          <Clock className="w-3 h-3 mr-1" />
          SLA {diffHours}시간 남음
        </span>
      );
    }
  }

  return (
    <div className="space-y-4">
      {/* Title & SLA Badge Header */}
      <div>
        <div className="flex items-start justify-between gap-3">
          <h2 className="text-xl font-bold text-slate-900 leading-snug">
            {ticket.title}
          </h2>
          {slaBadge}
        </div>

        {/* Metadata Bar */}
        <div className="flex flex-wrap items-center gap-y-2 gap-x-4 text-xs text-slate-500 mt-2 pb-3 border-b border-slate-100">
          <div className="flex items-center">
            <User className="w-3.5 h-3.5 mr-1 text-slate-400" />
            <span className="font-medium text-slate-700">작성자:</span>
            <span className="ml-1">{ticket.author_name || '사원'}</span>
          </div>
          <div className="flex items-center">
            <Calendar className="w-3.5 h-3.5 mr-1 text-slate-400" />
            <span className="font-medium text-slate-700">접수일시:</span>
            <span className="ml-1">
              {ticket.create_date ? new Date(ticket.create_date).toLocaleString() : '-'}
            </span>
          </div>
          <div className="flex items-center">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-slate-400" />
            <span className="font-medium text-slate-700">담당자:</span>
            <span className="ml-1 font-semibold text-slate-800">
              {ticket.assignee_name || '배정 대기'}
            </span>
          </div>
        </div>
      </div>

      {/* Inline Edit Form for Submitted Ticket */}
      {isEditingTicket && (
        <div className="p-4 bg-indigo-50/70 border border-indigo-200 rounded-xl space-y-3">
          <div className="text-xs font-bold text-indigo-900">문의 내용 수정</div>
          <form onSubmit={onSubmitEditTicket} className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">제목</label>
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                required
                className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">카테고리</label>
                <select
                  value={editCategory}
                  onChange={(e) => setEditCategory(e.target.value)}
                  className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="hw">하드웨어</option>
                  <option value="sw">소프트웨어</option>
                  <option value="network">네트워크</option>
                  <option value="account">계정/권한</option>
                  <option value="etc">기타</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">우선순위</label>
                <select
                  value={editPriority}
                  onChange={(e) => setEditPriority(e.target.value)}
                  className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="0">낮음</option>
                  <option value="1">보통</option>
                  <option value="2">높음</option>
                  <option value="3">긴급</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">상세 내용</label>
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                rows={4}
                required
                className="w-full text-sm px-3 py-2 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              />
            </div>
            {editTicketError && (
              <p className="text-xs text-rose-600 font-medium">{editTicketError}</p>
            )}
            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={onCancelEditTicket}
                className="px-3 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
              >
                취소
              </button>
              <button
                type="submit"
                disabled={submittingEditTicket}
                className="flex items-center px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 cursor-pointer transition-colors"
              >
                {submittingEditTicket && <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />}
                수정 완료
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Pending Banner (답변 대기 안내 배너) */}
      {ticket.status === 'pending' && (
        <div className="p-4 bg-purple-50 border border-purple-200 rounded-xl">
          <div className="flex items-center space-x-1.5">
            <HelpCircle className="w-4 h-4 text-purple-600 shrink-0" />
            <span className="text-xs font-bold text-purple-900 uppercase tracking-wider">
              IT 담당자 답변 대기 요청 안내
            </span>
          </div>
          <p className="text-xs text-purple-800 mt-1.5 whitespace-pre-wrap leading-relaxed">
            {ticket.pending_reason || '추가 확인 사항에 대한 사원님의 답변을 기다리고 있습니다.'}
          </p>

          {isAuthor && (
            <div className="mt-3 pt-3 border-t border-purple-200/80">
              {!showPendingReplyForm ? (
                <button
                  type="button"
                  onClick={onOpenPendingReply}
                  className="flex items-center text-xs font-semibold text-purple-700 bg-white border border-purple-300 hover:bg-purple-100/70 px-3 py-1.5 rounded-lg shadow-2xs transition-all cursor-pointer"
                >
                  <MessageSquare className="w-3.5 h-3.5 mr-1.5" />
                  요청 정보 답변 회신하기
                </button>
              ) : (
                <form onSubmit={onSubmitPendingReply} className="space-y-2 mt-2">
                  <textarea
                    value={pendingReplyText}
                    onChange={(e) => setPendingReplyText(e.target.value)}
                    placeholder="담당자가 요청한 추가 정보나 확인 내용을 입력해 주세요..."
                    rows={3}
                    className="w-full text-xs p-2.5 bg-white border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400 resize-none"
                    required
                  />
                  {pendingReplyError && (
                    <p className="text-xs text-rose-600 font-medium">{pendingReplyError}</p>
                  )}
                  <div className="flex justify-end space-x-2">
                    <button
                      type="button"
                      onClick={onClosePendingReply}
                      className="px-2.5 py-1 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
                    >
                      취소
                    </button>
                    <button
                      type="submit"
                      disabled={submittingPendingReply}
                      className="flex items-center px-3 py-1 text-xs font-semibold text-white bg-purple-600 hover:bg-purple-700 rounded-lg shadow-2xs cursor-pointer"
                    >
                      {submittingPendingReply && <Loader2 className="w-3 h-3 mr-1 animate-spin" />}
                      답변 회신 등록
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
