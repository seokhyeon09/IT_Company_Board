export interface EmailCategory {
  value: string;
  label: string;
  badgeClass: string;
}

const EMPLOYEE_CATEGORIES: EmailCategory[] = [
  { value: 'assigned', label: '담당자 배정', badgeClass: 'bg-blue-50 text-blue-700 border-blue-200' },
  { value: 'pending_request', label: '답변 대기 요청', badgeClass: 'bg-purple-50 text-purple-700 border-purple-200' },
  { value: 'resolved', label: '조치 완료 안내', badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
];

const OFFICER_CATEGORIES: EmailCategory[] = [
  { value: 'new_ticket', label: '신규 문의', badgeClass: 'bg-slate-100 text-slate-700 border-slate-200' },
  { value: 'assigned', label: '담당 배정', badgeClass: 'bg-blue-50 text-blue-700 border-blue-200' },
  { value: 'follow_up', label: '추가 회신', badgeClass: 'bg-amber-50 text-amber-800 border-amber-200' },
  { value: 'rated', label: '만족도 평가', badgeClass: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
];

export const getEmailCategories = (isOfficer: boolean): EmailCategory[] =>
  isOfficer ? OFFICER_CATEGORIES : EMPLOYEE_CATEGORIES;

export const findEmailCategory = (isOfficer: boolean, eventType: string): EmailCategory =>
  getEmailCategories(isOfficer).find((c) => c.value === eventType) || {
    value: eventType,
    label: eventType,
    badgeClass: 'bg-slate-100 text-slate-700 border-slate-200',
  };

export type ReadFilter = 'all' | 'unread' | 'read';
