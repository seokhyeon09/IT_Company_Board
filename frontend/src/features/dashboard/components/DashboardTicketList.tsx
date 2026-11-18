import React from 'react';
import { Inbox } from 'lucide-react';
import { TicketCard, Ticket } from '../../ticket/components/TicketCard';

export interface TicketSelectionConfig {
  selectable: boolean;
  selectedIds: number[];
  onToggleSelect: (ticketId: number) => void;
}

interface DashboardTicketListProps {
  loading: boolean;
  error: string | null;
  tickets: Ticket[];
  hasActiveFilters: boolean;
  onRetry: () => void;
  onResetFilters: () => void;
  onSelectTicket: (ticketId: number) => void;
  selection?: TicketSelectionConfig;
}

export const DashboardTicketList: React.FC<DashboardTicketListProps> = ({
  loading,
  error,
  tickets,
  hasActiveFilters,
  onRetry,
  onResetFilters,
  onSelectTicket,
  selection,
}) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-xl border border-slate-200 p-5 h-44 animate-pulse">
            <div className="h-4 bg-slate-100 rounded w-1/3 mb-4"></div>
            <div className="h-6 bg-slate-100 rounded w-3/4 mb-3"></div>
            <div className="h-3 bg-slate-100 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 bg-white rounded-2xl border border-rose-200">
        <p className="text-rose-600 font-medium text-sm">{error}</p>
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 px-3 py-1.5 rounded-lg cursor-pointer"
        >
          다시 시도
        </button>
      </div>
    );
  }

  if (tickets.length === 0) {
    return (
      <div className="text-center py-16 bg-white rounded-2xl border border-slate-200 shadow-xs">
        <Inbox className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-700 mb-1">티켓이 없습니다</h3>
        <p className="text-xs text-slate-400 mb-4">
          {hasActiveFilters
            ? '설정된 필터 조건에 부합하는 티켓이 없습니다. 필터를 초기화해 보세요.'
            : '등록된 문의가 없습니다. 새로운 문의를 등록해 보세요.'}
        </p>
        {hasActiveFilters && (
          <button
            type="button"
            onClick={onResetFilters}
            className="text-xs font-semibold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 px-3.5 py-1.5 rounded-lg cursor-pointer"
          >
            필터 초기화
          </button>
        )}
      </div>
    );
  }

  const selectedSet = new Set(selection?.selectedIds || []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {tickets.map((ticket: Ticket) => (
        <TicketCard
          key={ticket.id}
          ticket={ticket}
          onClick={(t) => onSelectTicket(t.id)}
          selectable={Boolean(selection?.selectable)}
          selected={selectedSet.has(ticket.id)}
          onToggleSelect={selection?.onToggleSelect}
        />
      ))}
    </div>
  );
};
