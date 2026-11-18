import React from 'react';
import { useAuthStore } from './stores/authStore';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { Navbar } from './components/Navbar';
import { ErrorBoundary } from './shared/components/ErrorBoundary';

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
