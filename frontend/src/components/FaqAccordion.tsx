import React, { useState } from 'react';
import { Ticket } from './TicketCard';
import {
  HelpCircle,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  ExternalLink,
  BookOpen,
  Tag,
  Search,
} from 'lucide-react';

interface FaqAccordionProps {
  tickets: Ticket[];
  onSelectTicket: (ticketId: number) => void;
}

const categoryMap: Record<string, string> = {
  hw: '하드웨어',
  sw: '소프트웨어',
  network: '네트워크',
  account: '계정/권한',
  etc: '기타',
};

export const FaqAccordion: React.FC<FaqAccordionProps> = ({ tickets, onSelectTicket }) => {
  const [openIds, setOpenIds] = useState<number[]>([]);

  const toggleAccordion = (id: number) => {
    setOpenIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  if (tickets.length === 0) {
    return (
      <div className="py-20 text-center bg-white rounded-3xl border border-slate-200 shadow-xs flex flex-col items-center justify-center p-6">
        <BookOpen className="w-12 h-12 text-slate-300 mb-3" />
        <h3 className="font-bold text-slate-800 text-base">등록된 공식 FAQ가 없습니다</h3>
        <p className="text-xs text-slate-400 mt-1 max-w-md">
          IT 지원팀에서 유용한 해결 사례를 FAQ 지식창고로 선정하면 이곳에 즉시 공유됩니다.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Banner */}
      <div className="p-4 bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-100 rounded-2xl flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-indigo-600 text-white rounded-xl shadow-xs">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900">사내 FAQ 지식창고</h4>
            <p className="text-xs text-slate-500 mt-0.5">
              자주 묻는 질문과 공식 해결 가이드를 확인하여 헬프데스크 접수 전 빠르게 문제를 해결해보세요.
            </p>
          </div>
        </div>
        <span className="text-xs font-bold text-indigo-700 bg-white border border-indigo-200 px-3 py-1 rounded-full shadow-xs">
          총 {tickets.length}개 가이드
        </span>
      </div>

      {/* Accordion List */}
      <div className="space-y-3">
        {tickets.map((t) => {
          const isOpen = openIds.includes(t.id);

          return (
            <div
              key={t.id}
              className={`bg-white rounded-2xl border transition-all overflow-hidden ${
                isOpen
                  ? 'border-indigo-300 shadow-md ring-1 ring-indigo-200'
                  : 'border-slate-200 hover:border-slate-300 shadow-xs'
              }`}
            >
              {/* Question Header */}
              <div
                onClick={() => toggleAccordion(t.id)}
                className="p-5 flex items-center justify-between cursor-pointer select-none bg-white hover:bg-slate-50/50 transition-colors"
              >
                <div className="flex items-start space-x-3.5 pr-4">
                  <div className="mt-0.5 p-1.5 bg-indigo-100 text-indigo-700 rounded-lg shrink-0">
                    <HelpCircle className="w-4 h-4" />
                  </div>

                  <div>
                    <div className="flex items-center space-x-2 mb-1.5">
                      <span className="font-mono text-[11px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                        {t.ticket_number}
                      </span>
                      <span className="text-[11px] font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded">
                        {categoryMap[t.category] || t.category}
                      </span>
                      <span className="text-[11px] text-slate-400">
                        담당자: {t.assignee_name || 'IT지원팀'}
                      </span>
                    </div>

                    <h3 className="font-bold text-sm text-slate-900 tracking-tight leading-snug">
                      {t.title}
                    </h3>
                  </div>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectTicket(t.id);
                    }}
                    className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                    title="티켓 상세 전체 보기"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </button>

                  <div className="p-1 text-slate-400">
                    {isOpen ? (
                      <ChevronUp className="w-5 h-5 text-indigo-600" />
                    ) : (
                      <ChevronDown className="w-5 h-5" />
                    )}
                  </div>
                </div>
              </div>

              {/* Accordion Answer Content */}
              {isOpen && (
                <div className="px-5 pb-5 pt-2 border-t border-slate-100 bg-slate-50/60 animate-in fade-in duration-150">
                  <div className="p-4 bg-emerald-50/90 border border-emerald-200 rounded-xl">
                    <div className="flex items-center text-emerald-800 font-bold text-xs uppercase tracking-wider mb-2">
                      <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-600" />
                      공식 해결 방법 및 조치 가이드
                    </div>
                    <div className="text-emerald-950 text-xs sm:text-sm leading-relaxed whitespace-pre-wrap">
                      자세한 문제 원인 및 해결 조치 절차는 상단의 [새 창 상세 보기] 아이콘을 클릭하여 원문 이력과 함께 확인하실 수 있습니다.
                    </div>
                  </div>

                  <div className="mt-3 flex justify-end">
                    <button
                      onClick={() => onSelectTicket(t.id)}
                      className="flex items-center text-xs font-bold text-indigo-600 hover:text-indigo-700 hover:underline cursor-pointer"
                    >
                      <span>원문 문의 및 전체 조치 히스토리 확인하기</span>
                      <ExternalLink className="w-3.5 h-3.5 ml-1" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
