import React from 'react';

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

  if (totalPages <= 1) {
    return null;
  }

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
    return [1, '...', page - 1, page, page + 1, '...', totalPages];
  };

  const pageNumbers = getPageNumbers();
  const startIdx = (page - 1) * pageSize + 1;
  const endIdx = Math.min(page * pageSize, total);

  return (
    <div className="flex items-center justify-between border-t border-slate-200/80 pt-4 mt-6">
      <span className="text-xs text-slate-500 font-medium">
        전체 {total}건 중 {startIdx}-{endIdx}건 표시
      </span>

      <div className="flex items-center space-x-1.5">
        <button
          type="button"
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          className="px-2.5 py-1 text-xs font-semibold text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-all"
        >
          이전
        </button>

        <div className="flex items-center space-x-1">
          {pageNumbers.map((item, idx) => {
            if (item === '...') {
              return (
                <span
                  key={`ellipsis-${idx}`}
                  className="text-slate-400 px-1 text-xs select-none"
                >
                  ...
                </span>
              );
            }
            const pageNum = item as number;
            const isActive = pageNum === page;
            return (
              <button
                key={pageNum}
                type="button"
                onClick={() => onPageChange(pageNum)}
                className={`w-7 h-7 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-2xs'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {pageNum}
              </button>
            );
          })}
        </div>

        <button
          type="button"
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="px-2.5 py-1 text-xs font-semibold text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-all"
        >
          다음
        </button>
      </div>
    </div>
  );
};
