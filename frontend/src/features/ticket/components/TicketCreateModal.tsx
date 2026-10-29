import React from 'react';
import { X, Send, AlertCircle, FileSpreadsheet, AlignLeft } from 'lucide-react';
import { useSimilarFaqs } from '../hooks/useSimilarFaqs';
import { useTicketCreateForm } from '../hooks/useTicketCreateForm';
import { CreateAttachmentField } from './create/CreateAttachmentField';
import { SimilarFaqList } from './create/SimilarFaqList';
import { TemplateFields } from './create/TemplateFields';

export interface TicketCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  onSelectTicket?: (ticketId: number) => void;
}

export const TicketCreateModal: React.FC<TicketCreateModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  onSelectTicket,
}) => {
  const form = useTicketCreateForm({ onSuccess, onClose });
  const { suggestedFaqs } = useSimilarFaqs(isOpen, form.category, form.title);

  if (!isOpen) return null;

  const hasCategoryTemplate = form.currentTemplate.fields.length > 0;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 animate-in fade-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <h2 className="text-lg font-bold text-slate-800">새 IT 문의 접수</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              도움이 필요한 내용을 자세히 작성해주시면 담당자가 배정됩니다.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {form.error && (
          <div
            data-testid="create-modal-error"
            className="mt-4 p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-start space-x-2 text-rose-700 text-xs"
          >
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{form.error}</span>
          </div>
        )}

        {form.notice && !form.error && (
          <div
            data-testid="create-modal-notice"
            className="mt-3 px-3 py-2 bg-slate-100 border border-slate-200 rounded-xl text-[11px] text-slate-600"
          >
            {form.notice}
          </div>
        )}

        <form onSubmit={form.handleSubmit} noValidate className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">제목</label>
            <input
              type="text"
              value={form.title}
              onChange={(e) => form.setTitle(e.target.value)}
              placeholder={form.currentTemplate.titlePlaceholder}
              className="w-full text-sm px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">분류</label>
              <select
                data-testid="create-category-select"
                value={form.category}
                onChange={(e) => form.handleCategoryChange(e.target.value)}
                className="w-full text-sm px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              >
                <option value="hw">하드웨어</option>
                <option value="sw">소프트웨어</option>
                <option value="network">네트워크</option>
                <option value="account">계정/권한</option>
                <option value="etc">기타</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">긴급도</label>
              <select
                data-testid="create-priority-select"
                value={form.priority}
                onChange={(e) => form.setPriority(e.target.value)}
                className="w-full text-sm px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              >
                <option value="0">낮음</option>
                <option value="1">보통</option>
                <option value="2">높음</option>
                <option value="3">긴급</option>
              </select>
            </div>
          </div>

          <SimilarFaqList
            suggestedFaqs={suggestedFaqs}
            onSelectFaq={(ticketId) => {
              if (onSelectTicket) {
                onClose();
                onSelectTicket(ticketId);
              }
            }}
          />

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-semibold text-slate-700">
                {form.useTemplateMode ? '분야별 맞춤 요청 양식' : '상세 내용'}
              </label>
              {hasCategoryTemplate && (
                <button
                  type="button"
                  data-testid="toggle-free-text-btn"
                  onClick={form.toggleFreeTextMode}
                  className="inline-flex items-center text-[11px] font-semibold text-indigo-600 hover:text-indigo-800 cursor-pointer"
                >
                  {form.isFreeText ? (
                    <>
                      <FileSpreadsheet className="w-3.5 h-3.5 mr-1" />
                      양식 템플릿으로 작성
                    </>
                  ) : (
                    <>
                      <AlignLeft className="w-3.5 h-3.5 mr-1" />
                      자유 입력으로 작성
                    </>
                  )}
                </button>
              )}
            </div>

            {form.useTemplateMode ? (
              <TemplateFields
                template={form.currentTemplate}
                values={form.templateValues}
                onChangeField={form.updateTemplateField}
                priorityHint={form.activePriorityHint}
              />
            ) : (
              <textarea
                data-testid="free-content-textarea"
                value={form.freeContent}
                onChange={(e) => form.setFreeContent(e.target.value)}
                placeholder="발생 증상, 시점, 에러 메시지 등을 가능한 상세히 적어주세요."
                rows={4}
                className="w-full text-sm px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all resize-none"
              />
            )}
          </div>

          <CreateAttachmentField
            attachments={form.attachments}
            onFileChange={form.handleFileChange}
            onRemoveAttachment={form.removeAttachment}
          />

          <div className="pt-3 border-t border-slate-100 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 rounded-xl hover:bg-slate-200 transition-colors cursor-pointer"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={form.loading}
              className="flex items-center px-4 py-2 text-xs font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 transition-colors cursor-pointer shadow-sm"
            >
              <Send className="w-3.5 h-3.5 mr-1.5" />
              {form.loading ? '접수 중...' : '문의 접수'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
