import { SlaBadgeInfo, SlaState } from '../types/common';

export const SLA_WARN_HOURS: Record<string, number> = {
  '3': 1,
  '2': 4,
  '1': 8,
  '0': 12,
};

export const formatSlaRemaining = (
  deadlineStr?: string,
  isOverdue?: boolean,
  status?: string,
  priority?: string,
  slaState?: SlaState | string
): SlaBadgeInfo | null => {
  if (!deadlineStr || ['resolved', 'closed', 'canceled'].includes(status || '')) {
    return null;
  }

  const deadline = new Date(deadlineStr).getTime();
  const now = Date.now();
  const diffMs = deadline - now;
  const isPast = diffMs < 0 || Boolean(isOverdue) || slaState === 'overdue';

  const absMinutes = Math.floor(Math.abs(diffMs) / (1000 * 60));
  const hours = Math.floor(absMinutes / 60);
  const minutes = absMinutes % 60;
  const days = Math.floor(hours / 24);

  let timeText = '';
  if (days > 0) {
    timeText = `${days}일 ${hours % 24}시간`;
  } else if (hours > 0) {
    timeText = `${hours}시간 ${minutes}분`;
  } else {
    timeText = `${minutes}분`;
  }

  if (isPast) {
    return {
      text: `SLA ${timeText} 초과`,
      badgeClass: 'bg-rose-100 text-rose-700 border-rose-300 font-semibold',
      isOverdue: true,
      isImminent: false,
    };
  }

  const warnHours = SLA_WARN_HOURS[priority || '0'] ?? 8;
  const isImminent =
    slaState === 'imminent' || diffMs <= warnHours * 60 * 60 * 1000;

  if (isImminent) {
    return {
      text: `SLA 임박 ${timeText} 남음`,
      badgeClass: 'bg-amber-100 text-amber-800 border-amber-300 font-semibold',
      isOverdue: false,
      isImminent: true,
    };
  }

  return {
    text: `SLA ${timeText} 남음`,
    badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    isOverdue: false,
    isImminent: false,
  };
};
