import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { apiClient } from '../api/client';
import { TicketCard, Ticket } from '../components/TicketCard';
import { TicketCreateModal } from '../components/TicketCreateModal';
import { Plus, Search, Filter, RefreshCw, BookOpen, Inbox } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Filters
  const [activeTab, setActiveTab] = useState<'all' | 'faq'>('all');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const params: any = {
        search: search.trim() || undefined,
        status: statusFilter || undefined,
        category: categoryFilter || undefined,
      };

      if (activeTab === 'faq') {
        params.is_faq = true;
      }

      const res = await apiClient.get('/tickets', { params });
      setTickets(res.data.data || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error('Failed to fetch tickets:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [activeTab, statusFilter, categoryFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchTickets();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Top Banner & Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">IT 지원 대시보드</h2>
          <p className="text-sm text-slate-500 mt-1">
            {user?.is_officer
              ? 'IT 담당자 전용: 전체 티켓 현황 및 조치 관리를 수행합니다.'
              : '사원 전용: 내 문의 내역 및 사내 FAQ 지식창고를 확인합니다.'}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchTickets}
            className="p-2.5 text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl transition-all shadow-sm"
            title="새로고침"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm rounded-xl shadow-md shadow-indigo-500/20 transition-all"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            새 문의 접수
          </button>
        </div>
      </div>

      {/* Tabs & Search Filter Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 mb-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Tabs */}
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'all'
                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            {user?.is_officer ? '전체 문의 목록' : '내 문의 내역'}
          </button>
          <button
            onClick={() => setActiveTab('faq')}
            className={`flex items-center px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'faq'
                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 mr-1.5" />
            FAQ 지식창고
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          <form onSubmit={handleSearchSubmit} className="relative">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="접수번호 또는 제목 검색..."
              className="pl-8 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 w-48 sm:w-64"
            />
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
          </form>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">전체 상태</option>
            <option value="submitted">접수대기</option>
            <option value="assigned">배정완료</option>
            <option value="in_progress">처리중</option>
            <option value="pending">답변대기</option>
            <option value="resolved">해결완료</option>
            <option value="closed">종결</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">전체 카테고리</option>
            <option value="hw">하드웨어</option>
            <option value="sw">소프트웨어</option>
            <option value="network">네트워크</option>
            <option value="account">계정/권한</option>
            <option value="etc">기타</option>
          </select>
        </div>
      </div>

      {/* Ticket Grid List */}
      {loading ? (
        <div className="py-20 text-center text-slate-400 text-sm flex flex-col items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-indigo-500 mb-3" />
          티켓 목록을 불러오는 중입니다...
        </div>
      ) : tickets.length === 0 ? (
        <div className="py-24 text-center bg-white rounded-3xl border border-slate-200 shadow-sm flex flex-col items-center justify-center">
          <Inbox className="w-12 h-12 text-slate-300 mb-3" />
          <h3 className="font-bold text-slate-700 text-base">조회된 문의 내역이 없습니다</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm">
            등록된 티켓이 없거나 조건에 일치하는 항목이 없습니다. 상단의 '새 문의 접수' 버튼을 눌러 티켓을 등록해보세요.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {tickets.map((ticket) => (
            <TicketCard
              key={ticket.id}
              ticket={ticket}
              onClick={(t) => {
                alert(`[${t.ticket_number}] ${t.title}\n상태: ${t.status}\n조치기한: ${t.deadline || '없음'}`);
              }}
            />
          ))}
        </div>
      )}

      {/* Ticket Create Modal */}
      <TicketCreateModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={fetchTickets}
      />
    </div>
  );
};
