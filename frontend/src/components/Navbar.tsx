import React from 'react';
import { useAuthStore } from '../stores/authStore';
import { ShieldCheck, User, LogOut, Layers } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuthStore();

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-indigo-600 text-white p-2 rounded-lg flex items-center justify-center shadow-sm">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-slate-900 tracking-tight">IT 헬프데스크</h1>
            <p className="text-xs text-slate-500">3-Tier Decoupled Architecture</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {user && (
            <div className="flex items-center space-x-3 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200">
              {user.is_admin || user.is_manager ? (
                <span className="flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-purple-100 text-purple-700">
                  <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                  IT 관리자
                </span>
              ) : user.is_officer ? (
                <span className="flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">
                  <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                  IT 담당자
                </span>
              ) : (
                <span className="flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
                  <User className="w-3.5 h-3.5 mr-1" />
                  일반 사원
                </span>
              )}
              <span className="text-sm font-medium text-slate-700">{user.name}</span>
            </div>
          )}

          <button
            onClick={logout}
            className="flex items-center text-xs font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 px-3 py-1.5 rounded-md transition-colors"
            title="로그아웃"
          >
            <LogOut className="w-4 h-4 mr-1.5" />
            로그아웃
          </button>
        </div>
      </div>
    </header>
  );
};
