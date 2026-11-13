import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query';
import { Banner } from './components/Banner';
import { Navbar } from './components/Navbar';
import { TraceDrawer } from './components/TraceDrawer';
import { Home } from './pages/Home';
import { ChaserCaseList } from './pages/ChaserCaseList';
import { ChaserCaseDetail } from './pages/ChaserCaseDetail';
import { TaskInbox } from './pages/TaskInbox';
import { AnalystFileList } from './pages/AnalystFileList';
import { AnalystFileReview } from './pages/AnalystFileReview';
import { MetricsPage } from './pages/MetricsPage';
import { GovernancePage } from './pages/GovernancePage';
import { EvalPage } from './pages/EvalPage';
import { adminApi } from './api/adminApi';
import { UserRole } from './types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 30, // 30s
      refetchOnWindowFocus: false,
    },
  },
});

function AppContent() {
  const [currentRole, setCurrentRole] = useState<UserRole>('RM');
  const [isTraceOpen, setIsTraceOpen] = useState(false);

  // Fetch simulated clock
  const { data: clockData, refetch: refetchClock } = useQuery({
    queryKey: ['simulatedClock'],
    queryFn: adminApi.getClock,
  });

  // Fetch agent runs for trace drawer
  const { data: agentRuns = [], refetch: refetchRuns } = useQuery({
    queryKey: ['agentRuns'],
    queryFn: adminApi.getAgentRuns,
    refetchInterval: isTraceOpen ? 3000 : false,
  });

  // Advance clock mutation
  const advanceClockMutation = useMutation({
    mutationFn: (days: number) => adminApi.advanceClock(days),
    onSuccess: (data) => {
      refetchClock();
      refetchRuns();
      queryClient.invalidateQueries({ queryKey: ['chaseCases'] });
      queryClient.invalidateQueries({ queryKey: ['reminderTasks'] });
      alert(`Advanced mock clock by ${data.advanced_business_days} business day(s) to ${data.new_date}. ${data.new_tasks_triggered_count} new task(s) triggered!`);
    },
  });

  // Reset demo mutation
  const resetDemoMutation = useMutation({
    mutationFn: adminApi.resetDemo,
    onSuccess: () => {
      refetchClock();
      refetchRuns();
      queryClient.invalidateQueries();
      alert('Demo data has been reset to initial baseline state.');
    },
  });

  const simulatedDate = clockData?.simulated_date || '2026-11-12';

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <Banner demoMode={true} simulatedDate={simulatedDate} />
      <Navbar
        currentRole={currentRole}
        onRoleChange={setCurrentRole}
        simulatedDate={simulatedDate}
        onAdvanceClock={(days) => advanceClockMutation.mutateAsync(days)}
        onResetDemo={() => resetDemoMutation.mutate()}
        onOpenTrace={() => setIsTraceOpen(true)}
        agentRunsCount={agentRuns.length}
      />

      <main className="flex-1 pb-16">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chaser" element={<ChaserCaseList />} />
          <Route path="/chaser/:id" element={<ChaserCaseDetail />} />
          <Route path="/tasks" element={<TaskInbox />} />
          <Route path="/analyst" element={<AnalystFileList />} />
          <Route path="/analyst/:id" element={<AnalystFileReview />} />
          <Route path="/metrics" element={<MetricsPage />} />
          <Route path="/governance" element={<GovernancePage />} />
          <Route path="/eval" element={<EvalPage />} />
        </Routes>
      </main>

      <TraceDrawer
        isOpen={isTraceOpen}
        onClose={() => setIsTraceOpen(false)}
        runs={agentRuns}
      />
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
