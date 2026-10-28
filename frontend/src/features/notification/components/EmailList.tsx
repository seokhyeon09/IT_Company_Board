import React from 'react';
import { EmailNotificationItem } from '../../ticket/types/ticket';
import { findEmailCategory } from '../emailCategories';

interface EmailListProps {
  items: EmailNotificationItem[];
  isOfficer: boolean;
  selectedId?: string;
  isRead: (id: string) => boolean;
  onSelect: (item: EmailNotificationItem) => void;
}

export const formatMailDate = (iso?: string) =>
  iso
    ? new Date(iso).toLocaleString('ko-KR', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
    : '-';

export const EmailList: React.FC<EmailListProps> = ({ items, isOfficer, selectedId, isRead, onSelect }) => (
  <div className="w-full md:w-5/12 border-b md:border-b-0 md:border-r border-slate-200 overflow-y-auto divide-y divide-slate-100 max-h-60 md:max-h-none">
    {items.map((item) => {
      const cat = findEmailCategory(isOfficer, item.event_type);
      const unread = !isRead(item.id);
      return (
        <button
          key={item.id}
          type="button"
          onClick={() => onSelect(item)}
          className={`w-full text-left p-3.5 transition-colors cursor-pointer ${
            selectedId === item.id ? 'bg-indigo-50/70' : 'hover:bg-slate-50'
          }`}
        >
          <div className="flex items-center justify-between gap-2 mb-1">
            <div className="flex items-center space-x-1.5">
              {unread && <span className="w-2 h-2 rounded-full bg-rose-500 shrink-0" title="미확인" />}
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${cat.badgeClass}`}>
                {cat.label}
              </span>
            </div>
            <span className="text-[11px] text-slate-400">{formatMailDate(item.sent_at)}</span>
          </div>
          <p className={`text-xs line-clamp-1 ${unread ? 'font-black text-slate-900' : 'font-medium text-slate-600'}`}>
            {item.subject}
          </p>
        </button>
      );
    })}
  </div>
);
