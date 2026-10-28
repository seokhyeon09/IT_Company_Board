import React, { useState, useEffect } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from 'lucide-react';

interface DashboardPaginationProps {
  page: number;
  total: number;
  pageSize: number;
  onPageChange: (newPage: number) => void;
}

const BLOCK_SIZE = 5;

export const DashboardPagination: React.FC<DashboardPaginationProps> = ({
  page,
  total,
  pageSize,
  onPageChange,
}) => {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const [jumpInput, setJumpInput] = useState(String(page));

  useEffect(() => {
    setJumpInput(String(page));
  }, [page]);

  // 5개 단위 블록 계산 (예: 1~5, 6~10, 11~15 ...)
  const currentBlock = Math.floor((page - 1) / BLOCK_SIZE);
  const startPage = currentBlock * BLOCK_SIZE + 1;
  const endPage = Math.min(startPage + BLOCK_SIZE - 1, totalPages);
  const prevBlockPage = startPage - BLOCK_SIZE;
  const nextBlockPage = startPage + BLOCK_SIZE;
  const hasPrevBlock = startPage > 1;
  const hasNextBlock = endPage < totalPages;

  const pageNumbers = Array.from(
    { length: endPage - startPage + 1 },
    (_, i) => startPage + i
  );

  const handleJumpSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const parsed = parseInt(jumpInput.trim(), 10);
    if (isNaN(parsed)) {
      setJumpInput(String(page));
      return;
    }
    const targetPage = Math.max(1, Math.min(totalPages, parsed));
    setJumpInput(String(targetPage));
    if (targetPage !== page) {
      onPageChange(targetPage);
    }
  };

  return (
    <div className="mt-8 flex flex-col lg:flex-row items-center justify-between gap-4 border-t border-slate-200 pt-6">
      <div className="text-xs text-slate-500 font-medium">
        전체 <span className="font-bold text-slate-900">{total}</span>개 중{' '}
        <span className="font-bold text-slate-900">
          {total > 0 ? (page - 1) * pageSize + 1 : 0}
        </span>
        -
        <span className="font-bold text-slate-900">
          {Math.min(page * pageSize, total)}
        </span>
        개 표시{' '}
        <span className="text-slate-400 ml-1">
          ({page} / {totalPages} 페이지)
        </span>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-2">
        {/* 처음 / 이전 블록 버튼 */}
        <div className="flex items-center space-x-1">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => onPageChange(1)}
            title="첫 페이지"
            className="flex items-center justify-center w-8 h-8 text-xs font-semibold rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
          >
            <ChevronsLeft className="w-4 h-4" />
          </button>
          <button
            type="button"
            disabled={!hasPrevBlock}
            onClick={() => onPageChange(Math.max(1, prevBlockPage))}
            title="이전 5개 페이지"
            className="flex items-center px-2.5 h-8 text-xs font-semibold rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
          >
            <ChevronLeft className="w-3.5 h-3.5 mr-0.5" />
            이전
          </button>
        </div>

        {/* 5개 단위 블록 페이지 번호 */}
        <div className="flex items-center space-x-1">
          {pageNumbers.map((pageNum) => (
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
          ))}
        </div>

        {/* 다음 블록 / 끝 버튼 */}
        <div className="flex items-center space-x-1">
          <button
            type="button"
            disabled={!hasNextBlock}
            onClick={() => onPageChange(Math.min(totalPages, nextBlockPage))}
            title="다음 5개 페이지"
            className="flex items-center px-2.5 h-8 text-xs font-semibold rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
          >
            다음
            <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
          </button>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => onPageChange(totalPages)}
            title="마지막 페이지"
            className="flex items-center justify-center w-8 h-8 text-xs font-semibold rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
          >
            <ChevronsRight className="w-4 h-4" />
          </button>
        </div>

        {/* 페이지 직접 입력 이동 */}
        <form
          onSubmit={handleJumpSubmit}
          className="flex items-center space-x-1.5 pl-2 border-l border-slate-200"
        >
          <input
            type="number"
            min={1}
            max={totalPages}
            value={jumpInput}
            onChange={(e) => setJumpInput(e.target.value)}
            aria-label="이동할 페이지 번호"
            className="w-14 h-8 px-2 text-xs text-center font-semibold border border-slate-200 rounded-xl bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
          <span className="text-xs text-slate-400 font-medium">/ {totalPages}</span>
          <button
            type="submit"
            className="px-2.5 h-8 text-xs font-semibold rounded-xl bg-slate-100 hover:bg-indigo-50 text-slate-700 hover:text-indigo-700 border border-slate-200 hover:border-indigo-200 transition-all cursor-pointer"
          >
            이동
          </button>
        </form>
      </div>
    </div>
  );
};
