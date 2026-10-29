import React from 'react';
import { HelpCircle, ArrowUpRight } from 'lucide-react';
import { SuggestedFaqTicket } from '../../types/ticketTemplate';

interface SimilarFaqListProps {
  suggestedFaqs: SuggestedFaqTicket[];
  onSelectFaq: (ticketId: number) => void;
}

export const SimilarFaqList: React.FC<SimilarFaqListProps> = ({
  suggestedFaqs,
  onSelectFaq,
}) => {
  if (suggestedFaqs.length === 0) return null;

  return (
    <div className="p-3 bg-indigo-50/60 border border-indigo-200/80 rounded-xl space-y-1.5">
      <div className="flex items-center justify-between">
        <span className="inline-flex items-center text-[11px] font-bold text-indigo-800">
          <HelpCircle className="w-3.5 h-3.5 mr-1 text-indigo-600" />
          유사 FAQ 및 해결 사례 추천 (접수 전 확인해보세요)
        </span>
        <span className="text-[10px] text-indigo-600 font-semibold">
          {suggestedFaqs.length}건
        </span>
      </div>
      <div className="space-y-1">
        {suggestedFaqs.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onSelectFaq(item.id)}
            className="w-full text-left px-2.5 py-1.5 bg-white hover:bg-indigo-50 rounded-lg border border-indigo-100 flex items-center justify-between text-xs transition-colors cursor-pointer group"
          >
            <div className="flex items-center space-x-2 truncate pr-2">
              <span className="px-1.5 py-0.2 bg-amber-100 text-amber-800 text-[10px] font-bold rounded shrink-0">
                FAQ
              </span>
              <span className="font-medium text-slate-700 group-hover:text-indigo-700 truncate">
                {item.title}
              </span>
            </div>
            <span className="inline-flex items-center text-[10px] font-semibold text-indigo-600 shrink-0">
              해결책 보기
              <ArrowUpRight className="w-3 h-3 ml-0.5" />
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};
