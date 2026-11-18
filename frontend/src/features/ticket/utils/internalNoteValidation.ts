export const MAX_INTERNAL_NOTE_LENGTH = 2000;

export interface InternalNoteValidationResult {
  valid: boolean;
  trimmed: string;
  error: string;
}

export function validateInternalNote(raw: string): InternalNoteValidationResult {
  const trimmed = String(raw || '').trim();
  if (!trimmed) {
    return {
      valid: false,
      trimmed: '',
      error: '내용을 입력해 주세요.',
    };
  }
  if (trimmed.length > MAX_INTERNAL_NOTE_LENGTH) {
    return {
      valid: false,
      trimmed,
      error: '메모는 최대 2000자까지 입력할 수 있습니다.',
    };
  }
  return {
    valid: true,
    trimmed,
    error: '',
  };
}
