import React, { useEffect, useRef, useState } from 'react';
import { CalendarOff, Loader2 } from 'lucide-react';
import { formatAbsenceLabel, todayIsoDate } from '../../../shared/utils/absenceUtils';
import { useOfficerAbsence } from '../hooks/useOfficerAbsence';

export const OfficerAbsenceControl: React.FC = () => {
  const { absence, saving, error, clearError, saveAbsence } = useOfficerAbsence();
  const [isOpen, setIsOpen] = useState(false);
  const [draftAbsent, setDraftAbsent] = useState(false);
  const [draftUntil, setDraftUntil] = useState('');
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    const handleMouseDown = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const handleToggleOpen = () => {
    if (!isOpen) {
      setDraftAbsent(absence.is_absent);
      setDraftUntil(absence.absent_until || '');
      clearError();
    }
    setIsOpen((prev) => !prev);
  };

  const handleSave = async () => {
    const ok = await saveAbsence({
      is_absent: draftAbsent,
      absent_until: draftAbsent && draftUntil ? draftUntil : null,
    });
    if (ok) {
      setIsOpen(false);
    }
  };

  const buttonLabel = absence.is_absent ? formatAbsenceLabel(absence) : '부재 설정';
  const minDate = todayIsoDate();

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={handleToggleOpen}
        aria-expanded={isOpen}
        className={`flex items-center whitespace-nowrap text-xs font-semibold px-3 py-2 rounded-xl border transition-all shadow-xs cursor-pointer ${
          absence.is_absent
            ? 'text-amber-800 bg-amber-50 hover:bg-amber-100 border-amber-300'
            : 'text-slate-600 bg-white hover:bg-slate-50 border-slate-200'
        }`}
      >
        <CalendarOff className="w-3.5 h-3.5 mr-1.5" />
        {buttonLabel}
      </button>

      {isOpen && (
        <div className="absolute left-0 sm:left-auto sm:right-0 mt-2 w-72 z-30 bg-white border border-slate-200 rounded-2xl shadow-xl p-4 space-y-3">
          <div className="text-xs font-bold text-slate-900">담당자 부재(휴가) 설정</div>

          <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
            <input
              type="checkbox"
              checked={draftAbsent}
              onChange={(e) => setDraftAbsent(e.target.checked)}
              className="rounded border-slate-300 text-amber-600 focus:ring-amber-500"
            />
            <span>부재 중으로 설정</span>
          </label>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              종료일(선택)
            </label>
            <input
              type="date"
              min={minDate}
              value={draftUntil}
              onChange={(e) => setDraftUntil(e.target.value)}
              className="w-full px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>

          <p className="text-[11px] text-slate-500 leading-relaxed">
            부재 중에는 자동 배정 대상에서 제외됩니다. 종료일이 지나면 자동으로 해제됩니다.
          </p>

          {error && <p className="text-xs text-rose-600 font-medium">{error}</p>}

          <div className="flex justify-end gap-2 pt-1">
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="px-2.5 py-1.5 text-xs text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 cursor-pointer"
            >
              취소
            </button>
            <button
              type="button"
              disabled={saving}
              onClick={handleSave}
              className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-white bg-amber-600 hover:bg-amber-700 rounded-lg disabled:opacity-50 cursor-pointer"
            >
              {saving && <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />}
              저장
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
