import React from 'react';
import { FileBarChart2, Loader2, X } from 'lucide-react';
import { useModalBehavior } from '../../../shared/hooks/useModalBehavior';
import { useSlaReport } from '../hooks/useSlaReport';
import { SlaReportBreakdownTables } from './SlaReportBreakdownTables';
import { SlaReportControls } from './SlaReportControls';
import { SlaReportKpiCards } from './SlaReportKpiCards';
import { SlaReportTrendChart } from './SlaReportTrendChart';

export interface SlaReportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SlaReportModal: React.FC<SlaReportModalProps> = ({ isOpen, onClose }) => {
  const report = useSlaReport(isOpen);
  useModalBehavior({ isOpen, onClose });

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] flex flex-col overflow-hidden border border-slate-100">
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-indigo-100 text-indigo-700 rounded-xl">
              <FileBarChart2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">기간별 SLA 운영 리포트</h3>
              <p className="text-xs text-slate-500">
                조회 기간: {report.dateFrom} ~ {report.dateTo} (KST 기준)
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="닫기"
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-5">
          <SlaReportControls
            preset={report.preset}
            unit={report.unit}
            category={report.category}
            exporting={report.exporting}
            exportError={report.exportError}
            onSelectPreset={report.selectPreset}
            onChangeUnit={report.changeUnit}
            onChangeCategory={report.setCategory}
            onExportCsv={report.exportCsv}
          />

          {report.loading ? (
            <div className="py-16 flex flex-col items-center justify-center text-slate-400">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-600 mb-2" />
              <p className="text-sm font-medium">SLA 리포트를 집계하는 중입니다...</p>
            </div>
          ) : report.error ? (
            <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-center text-sm">
              {report.error}
            </div>
          ) : !report.data ? (
            <div className="py-12 text-center text-sm text-slate-400">
              집계된 리포트 데이터가 없습니다.
            </div>
          ) : (
            <>
              <SlaReportKpiCards summary={report.data.summary} />
              <SlaReportTrendChart series={report.data.series} unit={report.data.range.unit} />
              <SlaReportBreakdownTables
                categories={report.data.by_category}
                priorities={report.data.by_priority}
              />
            </>
          )}
        </div>

        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-semibold text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
};
