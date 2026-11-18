const ISO_DATE_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;

export function formatShortMonthDay(isoDate?: string | null): string {
  if (!isoDate) return '';
  const match = isoDate.slice(0, 10).match(ISO_DATE_PATTERN);
  if (!match) return '';
  const month = Number(match[2]);
  const day = Number(match[3]);
  if (!month || !day) return '';
  return `${month}/${day}`;
}

export function formatAbsenceLabel(info: {
  is_absent?: boolean;
  absent_until?: string | null;
}): string {
  if (!info.is_absent) return '';
  const md = formatShortMonthDay(info.absent_until);
  return md ? `부재중 (~${md})` : '부재중';
}

/**
 * Returns local calendar date in YYYY-MM-DD format without UTC day shift.
 */
export function todayIsoDate(now: Date = new Date()): string {
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function isValidAbsenceUntil(
  value: string | null | undefined,
  today: string
): boolean {
  if (!value || !value.trim()) {
    return true;
  }
  const trimmed = value.trim();
  const match = trimmed.match(ISO_DATE_PATTERN);
  if (!match) {
    return false;
  }
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const parsed = new Date(year, month - 1, day);
  if (
    parsed.getFullYear() !== year ||
    parsed.getMonth() !== month - 1 ||
    parsed.getDate() !== day
  ) {
    return false;
  }
  return trimmed >= today;
}
