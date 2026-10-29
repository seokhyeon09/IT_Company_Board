export type TicketCategory = 'hw' | 'sw' | 'network' | 'account' | 'etc';
export type TicketPriority = '0' | '1' | '2' | '3';
export type TicketStatus =
  | 'submitted'
  | 'assigned'
  | 'in_progress'
  | 'pending'
  | 'resolved'
  | 'closed'
  | 'canceled';
export type TicketStatusFilter = TicketStatus | 'waiting' | 'overdue' | '';

export interface BadgeStyle {
  label: string;
  color: string;
}

export interface PriorityStyle {
  label: string;
  badge: string;
}

export type SlaState = 'none' | 'ok' | 'imminent' | 'overdue';

export interface SlaBadgeInfo {
  text: string;
  badgeClass: string;
  isOverdue: boolean;
  isImminent?: boolean;
}

export const statusMap: Record<string, BadgeStyle> = {
  submitted: { label: '접수대기', color: 'bg-amber-50 text-amber-700 border-amber-200' },
  assigned: { label: '배정완료', color: 'bg-blue-50 text-blue-700 border-blue-200' },
  in_progress: { label: '처리중', color: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  pending: { label: '답변대기', color: 'bg-purple-50 text-purple-700 border-purple-200' },
  resolved: { label: '해결완료', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  closed: { label: '종결', color: 'bg-slate-100 text-slate-600 border-slate-200' },
  canceled: { label: '취소', color: 'bg-rose-50 text-rose-700 border-rose-200' },
};

export const categoryMap: Record<string, string> = {
  hw: '하드웨어',
  sw: '소프트웨어',
  network: '네트워크',
  account: '계정/권한',
  etc: '기타',
};

export const priorityMap: Record<string, PriorityStyle> = {
  '3': { label: '긴급', badge: 'bg-rose-500 text-white' },
  '2': { label: '높음', badge: 'bg-orange-500 text-white' },
  '1': { label: '보통', badge: 'bg-slate-200 text-slate-700' },
  '0': { label: '낮음', badge: 'bg-slate-100 text-slate-500' },
};
