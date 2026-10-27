import React, { Component, ErrorInfo, ReactNode } from 'react';
import { useAuthStore } from './stores/authStore';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { Navbar } from './components/Navbar';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error caught by ErrorBoundary:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-3xl p-8 shadow-2xl border border-slate-200 text-center">
            <div className="inline-flex p-3 rounded-2xl bg-rose-50 text-rose-600 mb-4">
              <AlertTriangle className="w-8 h-8" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 mb-2">화면 로딩 중 오류가 발생했습니다</h2>
            <p className="text-xs text-slate-500 mb-4 bg-slate-50 p-3 rounded-xl font-mono text-left overflow-auto max-h-32">
              {this.state.error?.message || '알 수 없는 렌더링 오류'}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
              className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl flex items-center justify-center text-sm shadow-md transition-all"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              페이지 새로고침
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export const App: React.FC = () => {
  const { isAuthenticated } = useAuthStore();

  return (
    <ErrorBoundary>
      {!isAuthenticated ? (
        <LoginPage />
      ) : (
        <div className="min-h-screen bg-slate-50 flex flex-col">
          <Navbar />
          <main className="flex-1">
            <DashboardPage />
          </main>
        </div>
      )}
    </ErrorBoundary>
  );
};
