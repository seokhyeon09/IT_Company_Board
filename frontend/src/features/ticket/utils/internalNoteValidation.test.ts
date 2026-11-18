import { describe, it, expect } from 'vitest';
import { MAX_INTERNAL_NOTE_LENGTH, validateInternalNote } from './internalNoteValidation';

describe('internalNoteValidation', () => {
  it('rejects empty or whitespace-only content', () => {
    expect(validateInternalNote('')).toEqual({
      valid: false,
      trimmed: '',
      error: '내용을 입력해 주세요.',
    });
    expect(validateInternalNote('   \n\t  ')).toEqual({
      valid: false,
      trimmed: '',
      error: '내용을 입력해 주세요.',
    });
  });

  it('rejects content exceeding 2000 characters', () => {
    const over = '가'.repeat(MAX_INTERNAL_NOTE_LENGTH + 1);
    expect(validateInternalNote(over)).toEqual({
      valid: false,
      trimmed: over,
      error: '메모는 최대 2000자까지 입력할 수 있습니다.',
    });
  });

  it('trims valid content up to 2000 characters', () => {
    const exact = 'a'.repeat(MAX_INTERNAL_NOTE_LENGTH);
    expect(validateInternalNote(`  ${exact}  `)).toEqual({
      valid: true,
      trimmed: exact,
      error: '',
    });
  });
});
