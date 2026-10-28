import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface DashboardPaginationProps {
  page: number;
  total: number;
  pageSize: number;
  onPageChange: (newPage: number) => void;
}

export const DashboardPagination: React.FC<DashboardPaginationProps> = ({
  page,
  total,
  pageSize,
  onPageChange,
}) => {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const getPageNumbers = () => {
    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    if (page <= 4) {
      return [1, 2, 3, 4, 5, '...', totalPages];
    }
    if (page >= totalPages - 3) {
      return [
        1,
        '...',
        totalPages - 4,
        totalPages - 3,
        totalPages - 2,
        totalPages - 1,
        totalPages,
      ];
    }
    return [1, '...', page - 2, page - 1, page, page + 1, page + 2, '...', totalPages];
  };

  return (
    <div className="mt-8 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-200 pt-6">
      <div className="text-xs text-slate-500 font-medium">
        전체 <span className="font-bold text-slate-900">{total}</span>개 중{' '}
        <span className="font-bold text-slate-900">{(page - 1) * pageSize + 1}</span>-
        <span className="font-bold text-slate-900">{Math.min(page * pageSize, total)}</span>개 표시
      </div>

      <div className="flex items-center space-x-2">
        <button
          type="button"
          disabled={page <= 1}
          onClick={() => onPageChange(Math.max(1, page - 1))}
          className="flex items-center px-3 py-1.5 text-xs font-semibold rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
        >
          <ChevronLeft className="w-3.5 h-3.5 mr-1" />
          이전
        </button>

        <div className="flex items-center space-x-1">
          {getPageNumbers().map((item, idx) => {
            if (item === '...') {
              return (
                <span key={`ellipsis-${idx}`} className="text-slate-400 px-1 text-xs select-none">
                  ...
                </span>
              );
            }
            const pageNum = item as number;
            return (
              <button
                key={pageNum}
                type="button"
                onClick={() => onPageChange(pageNum)}
                className={`w-8 h-8 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  page === pageNum
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                {pageNum}
              </button>
            );
          })}
        </div>

        <button
          type="button"
          disabled={page >= totalPages}
          onClick={() => onPageChange(Math.min(totalPages, page + 1))}
          className="flex items-center px-3 py-1.5 text-xs font-semibold rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
        >
          다음
          <ChevronRight className="w-3.5 h-3.5 ml-1" />
        </button>
      </div>
    </div>
  );
};
