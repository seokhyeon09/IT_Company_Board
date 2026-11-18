import { useState, useEffect, useCallback } from 'react';
import { noteApi } from '../../../api/noteApi';
import { getErrorMessage } from '../../../api/client';
import { InternalNote } from '../types/ticket';
import { validateInternalNote } from '../utils/internalNoteValidation';

interface UseInternalNotesOptions {
  ticketId: number;
  initialNotes?: InternalNote[];
  onNoteAdded?: () => void;
}

export function useInternalNotes({
  ticketId,
  initialNotes,
  onNoteAdded,
}: UseInternalNotesOptions) {
  const [notes, setNotes] = useState<InternalNote[]>(initialNotes || []);
  const [draft, setDraft] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setNotes(initialNotes || []);
  }, [initialNotes]);

  useEffect(() => {
    setDraft('');
    setError('');
  }, [ticketId]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      const check = validateInternalNote(draft);
      if (!check.valid) {
        setError(check.error);
        return;
      }

      setSubmitting(true);
      setError('');
      try {
        const created = await noteApi.addNote(ticketId, check.trimmed);
        setNotes((prev) => [created, ...prev]);
        setDraft('');
        onNoteAdded?.();
      } catch (err) {
        setError(getErrorMessage(err, '내부 메모 저장에 실패했습니다.'));
      } finally {
        setSubmitting(false);
      }
    },
    [ticketId, draft, onNoteAdded]
  );

  return {
    notes,
    draft,
    setDraft,
    submitting,
    error,
    handleSubmit,
  };
}
