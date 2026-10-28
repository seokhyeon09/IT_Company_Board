import React, { useEffect, useMemo, useState } from 'react';
import { X, Mail, Loader2, Inbox } from 'lucide-react';
import { EmailNotificationItem } from '../../ticket/types/ticket';
import { getEmailCategories, ReadFilter } from '../emailCategories';
import { EmailFilterBar } from './EmailFilterBar';
import { EmailList } from './EmailList';
import { EmailPreview } from './EmailPreview';

export interface EmailNotificationModalProps {
  isOpen: boolean;
  isOfficer: boolean;
  items: EmailNotificationItem[];
  loading: boolean;
  error: string | null;
  isRead: (id: string) => boolean;
  onMarkRead: (id: string) => void;
  onMarkAllRead: () => void;
  onRefresh: () => void;
  onClose: () => void;
  onSelectTicket: (ticketId: number) => void;
}

export const EmailNotificationModal: React.FC<EmailNotificationModalProps> = ({
  isOpen,
  isOfficer,
  items,
  loading,
  error,
  isRead,
  onMarkRead,
  onMarkAllRead,
  onRefresh,
  onClose,
  onSelectTicket,
}) => {
  const [readFilter, setReadFilter] = useState<ReadFilter>('all');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [selected, setSelected] = useState<EmailNotificationItem | null>(null);

  useEffect(() => {
    if (isOpen) onRefresh();
  }, [isOpen]);

  const counts = useMemo(() => {
    const unread = items.filter((i) => !isRead(i.id)).length;
    return { all: items.length, unread, read: items.length - unread };
  }, [items, isRead]);

  const filtered = useMemo(
    () =>
      items.filter((i) => {
        if (categoryFilter && i.event_type !== categoryFilter) return false;
        if (readFilter === 'unread') return !isRead(i.id);
        if (readFilter === 'read') return isRead(i.id);
        return true;
      }),
    [items, readFilter, categoryFilter, isRead]
  );

  if (!isOpen) return null;

  const handleSelect = (item: EmailNotificationItem) => {
    setSelected(item);
    onMarkRead(item.id);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[88vh] flex flex-col overflow-hidden border border-slate-100">
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-indigo-600 text-white rounded-xl">
              <Mail className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">내 이메일 알림함 (모의 구현)</h2>
              <p className="text-xs text-slate-500">본인이 수신자인 알림 메일만 표시됩니다.</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/60 cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <EmailFilterBar
          categories={getEmailCategories(isOfficer)}
          readFilter={readFilter}
          onReadFilterChange={setReadFilter}
          categoryFilter={categoryFilter}
          onCategoryFilterChange={setCategoryFilter}
          counts={counts}
          onMarkAllRead={onMarkAllRead}
        />

        <div className="flex-1 overflow-hidden flex flex-col md:flex-row min-h-[380px]">
          {loading && items.length === 0 ? (
            <div className="w-full py-20 text-center text-slate-400 flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mb-3" />
              불러오는 중입니다...
            </div>
          ) : error ? (
            <div className="w-full p-6 text-center text-rose-700 text-xs font-semibold">{error}</div>
          ) : filtered.length === 0 ? (
            <div className="w-full py-20 text-center text-slate-400 flex flex-col items-center justify-center">
              <Inbox className="w-10 h-10 text-slate-300 mb-2" />
              <p className="text-sm font-semibold text-slate-600">조건에 해당하는 메일이 없습니다.</p>
            </div>
          ) : (
            <>
              <EmailList
                items={filtered}
                isOfficer={isOfficer}
                selectedId={selected?.id}
                isRead={isRead}
                onSelect={handleSelect}
              />
              <div className="w-full md:w-7/12 p-5 overflow-y-auto bg-slate-50/40">
                {selected ? (
                  <EmailPreview
                    mail={selected}
                    onOpenTicket={(id) => {
                      onClose();
                      onSelectTicket(id);
                    }}
                  />
                ) : (
                  <p className="text-xs text-slate-400 text-center pt-16">왼쪽 목록에서 메일을 선택하세요.</p>
                )}
              </div>
            </>
          )}
        </div>

        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 cursor-pointer"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
};
