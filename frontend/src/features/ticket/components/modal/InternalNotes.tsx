import React from 'react';
import { LockKeyhole, Send, Loader2 } from 'lucide-react';
import { InternalNote } from '../../types/ticket';
import { useInternalNotes } from '../../hooks/useInternalNotes';
import { MAX_INTERNAL_NOTE_LENGTH } from '../../utils/internalNoteValidation';

interface InternalNotesProps {
  ticketId: number;
  initialNotes?: InternalNote[];
  isOfficer: boolean;
  onNoteAdded?: () => void;
}

export const InternalNotes: React.FC<InternalNotesProps> = ({
  ticketId,
  initialNotes,
  isOfficer,
  onNoteAdded,
}) => {
  const { notes, draft, setDraft, submitting, error, handleSubmit } = useInternalNotes({
    ticketId,
    initialNotes,
    onNoteAdded,
  });

  if (!isOfficer) {
    return null;
  }

  const trimmedLen = draft.trim().length;
  const isOverLimit = trimmedLen > MAX_INTERNAL_NOTE_LENGTH;
  const canSubmit = trimmedLen > 0 && !isOverLimit && !submitting;

  return (
    <div className="pt-4 border-t border-slate-200 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-1.5">
          <LockKeyhole className="w-4 h-4 text-amber-600" />
          <h4 className="text-xs font-bold text-slate-800">
            내부 메모 (사원에게 보이지 않음)
          </h4>
          <span className="text-[11px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded">
            {notes.length}건
          </span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-2 bg-amber-50/50 border border-amber-200/80 rounded-xl p-3">
        <textarea
          rows={2}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="담당자/관리자끼리만 공유할 내부 메모를 입력하세요..."
          className="w-full px-3 py-2 text-xs bg-white border border-amber-200 rounded-lg text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-400 resize-y"
        />
        <div className="flex items-center justify-between gap-2">
          <span className={`text-[11px] ${isOverLimit ? 'text-rose-600 font-semibold' : 'text-slate-500'}`}>
            {draft.length} / {MAX_INTERNAL_NOTE_LENGTH}자
          </span>
          <button
            type="submit"
            disabled={!canSubmit}
            className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-white bg-amber-600 hover:bg-amber-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {submitting ? (
              <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
            ) : (
              <Send className="w-3.5 h-3.5 mr-1" />
            )}
            메모 추가
          </button>
        </div>
        {error && <p className="text-xs text-rose-600 font-medium">{error}</p>}
      </form>

      {notes.length === 0 ? (
        <p className="text-xs text-slate-400">등록된 내부 메모가 없습니다.</p>
      ) : (
        <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
          {notes.map((note) => (
            <div
              key={note.id}
              className="p-3 bg-amber-50/40 border border-amber-200/70 rounded-xl text-xs space-y-1"
            >
              <div className="flex items-center justify-between text-[11px] text-slate-500">
                <span className="font-semibold text-slate-700">{note.author_name}</span>
                <span>{note.date ? note.date.substring(0, 16).replace('T', ' ') : '-'}</span>
              </div>
              <p className="text-slate-800 whitespace-pre-wrap leading-relaxed">{note.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
