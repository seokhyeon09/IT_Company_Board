import React from 'react';
import { CheckCircle2, AlertCircle, X } from 'lucide-react';
import { BulkActionResult } from '../types/bulk';
import { extractBulkFailures, formatBulkSummaryText } from '../utils/bulkResult';

interface BulkResultBannerProps {
  result: BulkActionResult | null;
  onDismiss: () => void;
}

export const BulkResultBanner: React.FC<BulkResultBannerProps> = ({ result, onDismiss }) => {
  if (!result) return null;

  const failures = extractBulkFailures(result);
  const hasFailures = failures.length > 0;

  return (
    <div
      className={`p-3 rounded-xl border text-xs space-y-2 ${
        hasFailures
          ? 'bg-amber-50 border-amber-200 text-amber-900'
          : 'bg-emerald-50 border-emerald-200 text-emerald-900'
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 font-semibold">
          {hasFailures ? (
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          )}
          <span>{formatBulkSummaryText(result)}</span>
        </div>
        <button
          type="button"
          onClick={onDismiss}
          aria-label="결과 닫기"
          className="text-slate-500 hover:text-slate-700 cursor-pointer"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {hasFailures && (
        <ul className="space-y-1 pl-5 list-disc text-[11px] text-rose-700 max-h-28 overflow-y-auto">
          {failures.map((item) => (
            <li key={item.id}>
              <span className="font-mono font-semibold">{item.label}</span>: {item.message}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
