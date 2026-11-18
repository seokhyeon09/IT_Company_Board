import React, { useState } from 'react';
import { CheckSquare, UserCheck, Play, Lock } from 'lucide-react';
import { OfficerSimpleItem } from '../../ticket/types/ticket';
import { BulkActionPayload, BulkActionResult, BulkActionType, BulkPanelMode } from '../types/bulk';
import { areAllPageTicketsSelected } from '../utils/selection';
import { buildBulkPayload } from '../utils/bulkResult';
import { BulkActionSubPanel } from './BulkActionSubPanel';
import { BulkResultBanner } from './BulkResultBanner';

export interface BulkActionBarState {
  submitting: boolean;
  error: string;
  result: BulkActionResult | null;
  limitWarning: string;
  onTogglePageAll: () => void;
  onClearSelection: () => void;
  onExecuteBulk: (payload: BulkActionPayload) => Promise<BulkActionResult | null>;
  onDismissResult: () => void;
}

interface BulkActionBarProps {
  selectedIds: number[];
  pageTicketIds: number[];
  officers: OfficerSimpleItem[];
  state: BulkActionBarState;
}

export const BulkActionBar: React.FC<BulkActionBarProps> = ({
  selectedIds,
  pageTicketIds,
  officers,
  state,
}) => {
  const [panelMode, setPanelMode] = useState<BulkPanelMode>(null);

  if (pageTicketIds.length === 0 && selectedIds.length === 0 && !state.result) {
    return null;
  }

  const allPageSelected = areAllPageTicketsSelected(selectedIds, pageTicketIds);
  const hasSelection = selectedIds.length > 0;
  const actionsDisabled = !hasSelection || state.submitting;

  const handleTogglePanel = (mode: Exclude<BulkPanelMode, null>) => {
    setPanelMode((prev) => (prev === mode ? null : mode));
  };

  const handleExecute = async (params: {
    action: BulkActionType;
    officerId?: number | '';
    reason?: string;
    note?: string;
  }) => {
    const payload = buildBulkPayload({
      ticketIds: selectedIds,
      ...params,
    });
    const res = await state.onExecuteBulk(payload);
    if (res) {
      setPanelMode(null);
    }
  };

  return (
    <div className="mb-4 bg-white border border-slate-200 rounded-2xl p-3.5 shadow-xs space-y-2.5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center text-xs font-bold text-slate-800 bg-slate-100 px-2.5 py-1 rounded-lg">
            <CheckSquare className="w-3.5 h-3.5 mr-1.5 text-indigo-600" />
            선택 {selectedIds.length}건
          </span>

          <button
            type="button"
            onClick={state.onTogglePageAll}
            disabled={pageTicketIds.length === 0 || state.submitting}
            className="text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 px-2.5 py-1 rounded-lg cursor-pointer disabled:opacity-50"
          >
            {allPageSelected ? '현재 페이지 선택 해제' : '현재 페이지 전체 선택'}
          </button>

          {hasSelection && (
            <button
              type="button"
              onClick={() => {
                setPanelMode(null);
                state.onClearSelection();
              }}
              disabled={state.submitting}
              className="text-xs font-medium text-slate-600 hover:text-slate-800 px-2 py-1 rounded-lg hover:bg-slate-100 cursor-pointer"
            >
              선택 해제
            </button>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          <button
            type="button"
            disabled={actionsDisabled}
            onClick={() => handleTogglePanel('assign')}
            className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-emerald-700 bg-white border border-emerald-300 rounded-lg hover:bg-emerald-50 disabled:opacity-45 disabled:cursor-not-allowed cursor-pointer"
          >
            <UserCheck className="w-3.5 h-3.5 mr-1" />
            담당자 지정/인계
          </button>
          <button
            type="button"
            disabled={actionsDisabled}
            onClick={() => handleTogglePanel('start_progress')}
            className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-indigo-700 bg-white border border-indigo-300 rounded-lg hover:bg-indigo-50 disabled:opacity-45 disabled:cursor-not-allowed cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 mr-1" />
            처리 시작
          </button>
          <button
            type="button"
            disabled={actionsDisabled}
            onClick={() => handleTogglePanel('close')}
            className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-rose-700 bg-white border border-rose-300 rounded-lg hover:bg-rose-50 disabled:opacity-45 disabled:cursor-not-allowed cursor-pointer"
          >
            <Lock className="w-3.5 h-3.5 mr-1" />
            직권 종결
          </button>
        </div>
      </div>

      {state.limitWarning && (
        <p className="text-xs text-amber-700 font-medium">{state.limitWarning}</p>
      )}

      {state.error && <p className="text-xs text-rose-600 font-medium">{state.error}</p>}

      <BulkActionSubPanel
        panelMode={hasSelection ? panelMode : null}
        selectedCount={selectedIds.length}
        officers={officers}
        submitting={state.submitting}
        onExecute={handleExecute}
        onCancel={() => setPanelMode(null)}
      />

      <BulkResultBanner result={state.result} onDismiss={state.onDismissResult} />
    </div>
  );
};
