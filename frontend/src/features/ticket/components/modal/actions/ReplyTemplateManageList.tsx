import React, { useEffect, useRef, useState } from 'react';
import { Trash2 } from 'lucide-react';
import { categoryMap } from '../../../../../shared/types/common';
import { ReplyTemplate } from '../../../types/replyTemplate';

interface ReplyTemplateManageListProps {
  templates: ReplyTemplate[];
  deletingId: number | null;
  onRemove: (id: number) => Promise<boolean>;
}

export const ReplyTemplateManageList: React.FC<ReplyTemplateManageListProps> = ({
  templates,
  deletingId,
  onRemove,
}) => {
  const [confirmId, setConfirmId] = useState<number | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearConfirmTimer = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  useEffect(() => {
    return () => clearConfirmTimer();
  }, []);

  const handleDeleteClick = async (id: number) => {
    if (confirmId !== id) {
      clearConfirmTimer();
      setConfirmId(id);
      timerRef.current = setTimeout(() => {
        setConfirmId(null);
        timerRef.current = null;
      }, 3000);
      return;
    }

    clearConfirmTimer();
    setConfirmId(null);
    await onRemove(id);
  };

  if (templates.length === 0) {
    return (
      <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-[11px] text-slate-500">
        등록된 내 상용구가 없습니다.
      </div>
    );
  }

  return (
    <ul className="divide-y divide-slate-100 border border-slate-200 rounded-lg bg-white max-h-40 overflow-y-auto">
      {templates.map((tpl) => {
        const isConfirming = confirmId === tpl.id;
        const isDeleting = deletingId === tpl.id;
        const catLabel = tpl.category ? categoryMap[tpl.category] || tpl.category : '공통';
        return (
          <li
            key={tpl.id}
            className="flex items-center justify-between gap-2 px-2.5 py-1.5 text-[11px]"
          >
            <span className="truncate text-slate-700">
              <span className="font-semibold text-slate-500 mr-1">[{catLabel}]</span>
              {tpl.name}
            </span>
            <button
              type="button"
              disabled={isDeleting}
              onClick={() => handleDeleteClick(tpl.id)}
              className={`shrink-0 inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold transition-colors cursor-pointer disabled:opacity-50 ${
                isConfirming
                  ? 'bg-rose-600 text-white hover:bg-rose-700'
                  : 'text-rose-600 hover:bg-rose-50 border border-rose-200'
              }`}
            >
              <Trash2 className="w-3 h-3 mr-1" />
              {isDeleting ? '삭제 중...' : isConfirming ? '삭제 확인' : '삭제'}
            </button>
          </li>
        );
      })}
    </ul>
  );
};
