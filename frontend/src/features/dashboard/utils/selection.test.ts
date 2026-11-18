import { describe, it, expect } from 'vitest';
import {
  MAX_BULK_SELECTION,
  areAllPageTicketsSelected,
  deselectPageTickets,
  removeSucceededIds,
  selectPageTickets,
  toggleSelection,
} from './selection';

describe('selection utils', () => {
  it('toggles ticket id on and off', () => {
    const added = toggleSelection([1, 2], 3);
    expect(added).toEqual({ ids: [1, 2, 3], limitReached: false });

    const removed = toggleSelection([1, 2, 3], 2);
    expect(removed).toEqual({ ids: [1, 3], limitReached: false });
  });

  it('enforces max 50 selection limit on toggle and page select', () => {
    const fifty = Array.from({ length: MAX_BULK_SELECTION }, (_, i) => i + 1);
    const overToggle = toggleSelection(fifty, 51);
    expect(overToggle).toEqual({ ids: fifty, limitReached: true });

    const partial = Array.from({ length: 48 }, (_, i) => i + 1);
    const overPage = selectPageTickets(partial, [49, 50, 51, 52]);
    expect(overPage.ids).toHaveLength(50);
    expect(overPage.ids.slice(-2)).toEqual([49, 50]);
    expect(overPage.limitReached).toBe(true);
  });

  it('selects and deselects current page without dropping other pages', () => {
    const selected = selectPageTickets([100], [1, 2, 3]);
    expect(selected).toEqual({ ids: [100, 1, 2, 3], limitReached: false });
    expect(areAllPageTicketsSelected(selected.ids, [1, 2, 3])).toBe(true);
    expect(areAllPageTicketsSelected(selected.ids, [1, 2, 4])).toBe(false);
    expect(areAllPageTicketsSelected(selected.ids, [])).toBe(false);

    const deselected = deselectPageTickets(selected.ids, [1, 2, 3]);
    expect(deselected).toEqual([100]);
  });

  it('removes succeeded ids and keeps failed ids', () => {
    const next = removeSucceededIds([1, 2, 3], [
      { id: 1, ticket_number: 'TKT-1', ok: true, message: '처리되었습니다.' },
      { id: 2, ticket_number: 'TKT-2', ok: false, message: '실패' },
      { id: 3, ticket_number: 'TKT-3', ok: true, message: '처리되었습니다.' },
    ]);
    expect(next).toEqual([2]);
  });
});
