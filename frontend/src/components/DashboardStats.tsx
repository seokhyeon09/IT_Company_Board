import React from 'react';
import {
  Layers,
  Clock,
  Activity,
  PauseCircle,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';

export interface TicketStats {
  total: number;
  waiting: number;
  in_progress: number;
  pending: number;
  resolved: number;
  overdue: number;
}

interface DashboardStatsProps {
  stats: TicketStats | null;
  selectedStatus: string;
  onSelectStatus: (status: string) => void;
}

export const DashboardStats: React.FC<DashboardStatsProps> = ({
  stats,
  selectedStatus,
  onSelectStatus,
}) => {
  const cards = [
    {
      id: '',
      title: '전체 문의',
      count: stats?.total ?? 0,
      icon: Layers,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      activeRing: 'ring-2 ring-indigo-500 bg-indigo-50/50',
    },
    {
      id: 'waiting',
      title: '접수 / 배정',
      count: stats?.waiting ?? 0,
      icon: Clock,
      color: 'text-amber-600',
      bgColor: 'bg-amber-50',
      activeRing: 'ring-2 ring-amber-500 bg-amber-50/50',
    },
    {
      id: 'in_progress',
      title: '처리 중',
      count: stats?.in_progress ?? 0,
      icon: Activity,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      activeRing: 'ring-2 ring-blue-500 bg-blue-50/50',
    },
    {
      id: 'pending',
      title: '답변 대기',
      count: stats?.pending ?? 0,
      icon: PauseCircle,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      activeRing: 'ring-2 ring-purple-500 bg-purple-50/50',
    },
    {
      id: 'resolved',
      title: '해결 완료',
      count: stats?.resolved ?? 0,
      icon: CheckCircle2,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
      activeRing: 'ring-2 ring-emerald-500 bg-emerald-50/50',
    },
    {
      id: 'overdue',
      title: '기한 초과',
      count: stats?.overdue ?? 0,
      icon: AlertTriangle,
      color: 'text-rose-600',
      bgColor: 'bg-rose-50',
      activeRing: 'ring-2 ring-rose-500 bg-rose-50/50',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5 mb-8">
      {cards.map((card) => {
        const Icon = card.icon;
        const isSelected = selectedStatus === card.id;

        return (
          <button
            key={card.id}
            type="button"
            onClick={() => onSelectStatus(card.id)}
            className={`p-4 rounded-2xl border text-left transition-all bg-white shadow-xs hover:shadow-md cursor-pointer ${
              isSelected
                ? `${card.activeRing} border-transparent`
                : 'border-slate-200 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 tracking-tight">
                {card.title}
              </span>
              <div className={`p-2 rounded-xl ${card.bgColor} ${card.color}`}>
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-black text-slate-900 tracking-tight">
              {card.count.toLocaleString()}
              <span className="text-xs font-normal text-slate-400 ml-1">건</span>
            </div>
          </button>
        );
      })}
    </div>
  );
};
