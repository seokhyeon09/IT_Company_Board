import React, { useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { apiClient, getErrorMessage } from '../api/client';
import { Layers, Lock, User, AlertCircle, ArrowRight } from 'lucide-react';

const TEST_ACCOUNTS = [
  { role: 'IT 관리자', name: '최관리', email: 'admin@helpdesk.com', pw: 'admin', color: 'text-purple-600', badge: 'bg-purple-100 text-purple-700' },
  { role: '담당 (인프라)', name: '김담당', email: 'officer@test.com', pw: '1234', color: 'text-indigo-600', badge: 'bg-indigo-100 text-indigo-700' },
  { role: '담당 (보안/NW)', name: '박엔지니어', email: 'officer2@test.com', pw: '1234', color: 'text-indigo-600', badge: 'bg-indigo-100 text-indigo-700' },
  { role: '담당 (SW/라이선스)', name: '최소프트', email: 'officer3@test.com', pw: '1234', color: 'text-indigo-600', badge: 'bg-indigo-100 text-indigo-700' },
  { role: '담당 (계정/권한)', name: '한계정', email: 'officer4@test.com', pw: '1234', color: 'text-indigo-600', badge: 'bg-indigo-100 text-indigo-700' },
  { role: '담당 (총무/기타)', name: '오기타', email: 'officer5@test.com', pw: '1234', color: 'text-indigo-600', badge: 'bg-indigo-100 text-indigo-700' },
  { role: '사원 1 (개발)', name: '이개발', email: 'user1@test.com', pw: '1234', color: 'text-emerald-600', badge: 'bg-emerald-100 text-emerald-700' },
  { role: '사원 2 (기획)', name: '정기획', email: 'user2@test.com', pw: '1234', color: 'text-emerald-600', badge: 'bg-emerald-100 text-emerald-700' },
];

export const LoginPage: React.FC = () => {
  const [loginId, setLoginId] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setAuth = useAuthStore((state) => state.setAuth);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await apiClient.post('/auth/login', {
        login: loginId,
        password: password,
      });

      const { access_token, user } = res.data;
      setAuth(access_token, user);
    } catch (err: any) {
      setError(getErrorMessage(err, '로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-3xl shadow-2xl p-8 border border-slate-800">
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-indigo-50 text-indigo-600 mb-3 shadow-sm">
            <Layers className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">IT 헬프데스크 로그인</h2>
          <p className="text-xs text-slate-500 mt-1">3-Tier Decoupled Architecture</p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-center text-rose-700 text-xs">
            <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">아이디 (ID / Email)</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <User className="w-4 h-4" />
              </span>
              <input
                type="text"
                value={loginId}
                onChange={(e) => setLoginId(e.target.value)}
                placeholder="예: user1@test.com"
                className="w-full pl-10 pr-3 py-2.5 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">비밀번호 (Password)</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <Lock className="w-4 h-4" />
              </span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="비밀번호 입력"
                className="w-full pl-10 pr-3 py-2.5 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-indigo-500/25 flex items-center justify-center transition-all disabled:opacity-50"
          >
            <span>{loading ? '로그인 처리 중...' : '시스템 접속'}</span>
            <ArrowRight className="w-4 h-4 ml-2" />
          </button>
        </form>

        {/* Quick Test Account Selector */}
        <div className="mt-5 pt-4 border-t border-slate-100">
          <p className="text-xs font-bold text-slate-500 mb-2 text-center">
            테스트 계정 빠른 선택 (8인 전체)
          </p>
          <div className="grid grid-cols-2 gap-1.5 max-h-56 overflow-y-auto pr-1">
            {TEST_ACCOUNTS.map((acc) => (
              <button
                key={acc.email}
                type="button"
                onClick={() => {
                  setLoginId(acc.email);
                  setPassword(acc.pw);
                }}
                className="p-2 bg-slate-50 hover:bg-indigo-50/70 hover:border-indigo-200 border border-slate-200 rounded-xl text-left transition-all cursor-pointer"
              >
                <div className="flex items-center justify-between mb-0.5">
                  <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${acc.badge}`}>
                    {acc.role}
                  </span>
                  <span className="text-[10px] text-slate-400 font-medium">{acc.name}</span>
                </div>
                <div className="text-[10px] text-slate-500 font-mono truncate">{acc.email}</div>
                <div className={`text-[10px] font-semibold mt-0.5 ${acc.color}`}>비번: {acc.pw}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="mt-4 text-center">
          <p className="text-xs text-slate-400">
            사내 포털 계정(Odoo DB)으로 자동 인증 및 Bearer JWT가 발급됩니다.
          </p>
        </div>
      </div>
    </div>
  );
};
