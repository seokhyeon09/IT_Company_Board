import React from 'react';
import { CheckCheck } from 'lucide-react';
import { EmailCategory, ReadFilter } from '../emailCategories';

interface EmailFilterBarProps {
  categories: EmailCategory[];
  readFilter: ReadFilter;
  onReadFilterChange: (v: ReadFilter) => void;
  categoryFilter: string;
  onCategoryFilterChange: (v: string) => void;
  counts: { all: number; unread: number; read: number };
  onMarkAllRead: () => void;
}

const READ_TABS: { value: ReadFilter; label: string; key: 'all' | 'unread' | 'read' }[] = [
  { value: 'all', label: '전체', key: 'all' },
  { value: 'unread', label: '미확인', key: 'unread' },
  { value: 'read', label: '확인', key: 'read' },
];

export const EmailFilterBar: React.FC<EmailFilterBarProps> = ({
  categories,
  readFilter,
  onReadFilterChange,
  categoryFilter,
  onCategoryFilterChange,
  counts,
  onMarkAllRead,
}) => (
  <div className="px-6 py-3 border-b border-slate-200 space-y-2.5 bg-white">
    <div className="flex items-center justify-between">
      <div className="flex space-x-1.5">
        {READ_TABS.map((t) => (
          <button
            key={t.value}
            type="button"
            onClick={() => onReadFilterChange(t.value)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              readFilter === t.value
                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            {t.label} ({counts[t.key]})
          </button>
        ))}
      </div>
      <button
        type="button"
        onClick={onMarkAllRead}
        disabled={counts.unread === 0}
        className="flex items-center text-xs font-semibold text-slate-500 hover:text-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed px-2 py-1 rounded-lg hover:bg-slate-100 cursor-pointer"
      >
        <CheckCheck className="w-3.5 h-3.5 mr-1" />
        모두 확인 처리
      </button>
    </div>
    <div className="flex flex-wrap gap-1.5">
      {[{ value: '', label: '전체 유형' }, ...categories].map((c) => (
        <button
          key={c.value || 'all'}
          type="button"
          onClick={() => onCategoryFilterChange(c.value)}
          className={`px-2.5 py-1 rounded-full text-[11px] font-semibold border transition-all cursor-pointer ${
            categoryFilter === c.value
              ? 'bg-slate-800 text-white border-slate-800'
              : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
          }`}
        >
          {c.label}
        </button>
      ))}
    </div>
  </div>
);
