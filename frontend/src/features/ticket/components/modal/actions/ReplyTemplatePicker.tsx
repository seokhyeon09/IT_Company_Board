import React, { useState } from 'react';
import { BookmarkPlus, ChevronDown, ChevronUp } from 'lucide-react';
import {
  TicketCategory,
  VALID_TICKET_CATEGORIES,
  categoryMap,
} from '../../../../../shared/types/common';
import { useAuthStore } from '../../../../../stores/authStore';
import { useReplyTemplates } from '../../../hooks/useReplyTemplates';
import { ReplyTemplateCategory } from '../../../types/replyTemplate';
import { applyTemplateVariables } from '../../../utils/replyTemplateText';
import { ReplyTemplateManageList } from './ReplyTemplateManageList';

interface ReplyTemplatePickerProps {
  category: string;
  ticketNumber: string;
  requesterName?: string;
  currentText: string;
  onInsert: (text: string) => void;
}

function toValidCategory(value: string): TicketCategory | '' {
  return (VALID_TICKET_CATEGORIES as readonly string[]).includes(value)
    ? (value as TicketCategory)
    : '';
}

export const ReplyTemplatePicker: React.FC<ReplyTemplatePickerProps> = ({
  category,
  ticketNumber,
  requesterName,
  currentText,
  onInsert,
}) => {
  const user = useAuthStore((s) => s.user);
  const { templates, loading, saving, deletingId, error, clearError, save, remove } =
    useReplyTemplates(category);

  const ticketCategory = toValidCategory(category);
  const [selectedId, setSelectedId] = useState('');
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [showManage, setShowManage] = useState(false);
  const [draftName, setDraftName] = useState('');
  const [draftCategory, setDraftCategory] = useState<ReplyTemplateCategory>(ticketCategory);

  const myTemplates = templates.filter((t) => t.is_mine);
  const hasContent = Boolean(currentText.trim());

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const idStr = e.target.value;
    setSelectedId('');
    if (!idStr) return;
    const found = templates.find((t) => String(t.id) === idStr);
    if (!found) return;
    const expanded = applyTemplateVariables(found.body, {
      requester_name: requesterName,
      ticket_number: ticketNumber,
      officer_name: user?.name,
    });
    onInsert(expanded);
  };

  const handleToggleSaveForm = () => {
    clearError();
    if (!showSaveForm) {
      setDraftName('');
      setDraftCategory(ticketCategory);
    }
    setShowSaveForm((prev) => !prev);
  };

  const handleSaveTemplate = async () => {
    const trimmedName = draftName.trim();
    const trimmedBody = currentText.trim();
    if (!trimmedName || !trimmedBody) return;
    const ok = await save({
      name: trimmedName.slice(0, 60),
      category: draftCategory,
      body: currentText,
    });
    if (ok) {
      setShowSaveForm(false);
      setDraftName('');
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-2">
        <select
          aria-label="상용구"
          value={selectedId}
          disabled={loading}
          onChange={handleSelectChange}
          className="text-xs border border-slate-300 rounded-lg px-2.5 py-1.5 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer max-w-[220px]"
        >
          <option value="">상용구 불러오기</option>
          {templates.map((tpl) => {
            const catLabel = tpl.category ? categoryMap[tpl.category] || tpl.category : '공통';
            return (
              <option key={tpl.id} value={String(tpl.id)}>
                [{catLabel}] {tpl.name}
              </option>
            );
          })}
        </select>

        <button
          type="button"
          disabled={!hasContent}
          onClick={handleToggleSaveForm}
          className="inline-flex items-center px-2.5 py-1.5 text-[11px] font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <BookmarkPlus className="w-3.5 h-3.5 mr-1" />
          현재 내용을 상용구로 저장
        </button>

        <button
          type="button"
          onClick={() => {
            clearError();
            setShowManage((prev) => !prev);
          }}
          className="inline-flex items-center px-2 py-1.5 text-[11px] font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
        >
          내 상용구 관리 ({myTemplates.length})
          {showManage ? (
            <ChevronUp className="w-3.5 h-3.5 ml-0.5" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 ml-0.5" />
          )}
        </button>
      </div>

      {showSaveForm && (
        <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg space-y-2">
          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              maxLength={60}
              value={draftName}
              onChange={(e) => setDraftName(e.target.value)}
              placeholder="상용구 이름 (최대 60자)"
              className="flex-1 px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-800"
            />
            <select
              value={draftCategory}
              onChange={(e) => setDraftCategory(e.target.value as ReplyTemplateCategory)}
              className="px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700 cursor-pointer"
            >
              {ticketCategory && (
                <option value={ticketCategory}>
                  이 티켓 분야 ({categoryMap[ticketCategory] || ticketCategory})
                </option>
              )}
              <option value="">공통</option>
            </select>
          </div>
          <div className="flex justify-end gap-1.5">
            <button
              type="button"
              onClick={() => setShowSaveForm(false)}
              className="px-2.5 py-1 text-[11px] text-slate-600 bg-white border border-slate-200 rounded-md hover:bg-slate-100 cursor-pointer"
            >
              취소
            </button>
            <button
              type="button"
              disabled={!hasContent || !draftName.trim() || saving}
              onClick={handleSaveTemplate}
              className="px-2.5 py-1 text-[11px] font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-md disabled:opacity-50 cursor-pointer"
            >
              {saving ? '저장 중...' : '저장'}
            </button>
          </div>
        </div>
      )}

      {showManage && (
        <ReplyTemplateManageList
          templates={myTemplates}
          deletingId={deletingId}
          onRemove={remove}
        />
      )}

      {error && <p className="text-[11px] text-rose-600 font-medium">{error}</p>}
    </div>
  );
};
