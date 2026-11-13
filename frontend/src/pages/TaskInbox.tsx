import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { NavLink } from 'react-router-dom';
import { chaseApi } from '../api/chaseApi';
import { ReminderTask } from '../types';
import {
  CheckSquare,
  Clock,
  PhoneCall,
  Mail,
  AlertOctagon,
  ArrowRight,
  CheckCircle2,
  Calendar,
  RefreshCw,
  Moon
} from 'lucide-react';

export const TaskInbox: React.FC = () => {
  const queryClient = useQueryClient();
  const [snoozeModalTask, setSnoozeModalTask] = useState<ReminderTask | null>(null);
  const [snoozeDays, setSnoozeDays] = useState(1);
  const [snoozeReason, setSnoozeReason] = useState('Client requested more time to retrieve records');

  const { data: tasks, isLoading, error, refetch } = useQuery({
    queryKey: ['reminderTasks'],
    queryFn: chaseApi.listTasks,
  });

  const completeMutation = useMutation({
    mutationFn: (taskId: number) => chaseApi.completeTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminderTasks'] });
      queryClient.invalidateQueries({ queryKey: ['chaseCases'] });
    },
  });

  const snoozeMutation = useMutation({
    mutationFn: ({ taskId, snooze_days, reason }: { taskId: number; snooze_days: number; reason: string }) =>
      chaseApi.snoozeTask(taskId, { snooze_days, reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reminderTasks'] });
      setSnoozeModalTask(null);
    },
  });

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 text-center text-slate-500">
        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
        <span>Loading task inbox...</span>
      </div>
    );
  }

  const getTaskIcon = (type: string, day: number) => {
    switch (type) {
      case 'email_reminder':
        return <Mail className="w-5 h-5 text-blue-600" />;
      case 'phone_call':
        return <PhoneCall className="w-5 h-5 text-amber-600" />;
      case 'manager_flag':
        return <AlertOctagon className="w-5 h-5 text-rose-600" />;
      default:
        return <CheckSquare className="w-5 h-5 text-slate-600" />;
    }
  };

  const getDayBadge = (day: number) => {
    switch (day) {
      case 3:
        return <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2 py-0.5 rounded">Day 3 Rule</span>;
      case 6:
        return <span className="bg-amber-100 text-amber-900 text-xs font-bold px-2 py-0.5 rounded">Day 6 Rule</span>;
      case 9:
        return <span className="bg-rose-100 text-rose-900 text-xs font-bold px-2 py-0.5 rounded">Day 9 Stalled</span>;
      default:
        return null;
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs uppercase font-mono font-bold text-blue-600 tracking-wider">Module A Cadence</span>
          <h1 className="text-2xl font-bold text-slate-900">Relationship Manager Task Inbox</h1>
          <p className="text-xs text-slate-500 mt-1">
            Automated follow-up triggers fired by business calendar cadence: Day 3 email, Day 6 phone call, Day 9 ops flag.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          className="inline-flex items-center space-x-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded px-3 py-1.5 hover:bg-slate-50 shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Tasks</span>
        </button>
      </div>

      {/* Task Cards List */}
      <div className="space-y-4">
        {tasks && tasks.length > 0 ? (
          tasks.map((task) => (
            <div
              key={task.id}
              className={`bg-white rounded-xl border p-5 shadow-sm space-y-3 transition ${
                task.task_type === 'manager_flag'
                  ? 'border-rose-300 bg-rose-50/20'
                  : task.task_type === 'phone_call'
                  ? 'border-amber-300 bg-amber-50/10'
                  : 'border-slate-200'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center space-x-3">
                  <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 shrink-0">
                    {getTaskIcon(task.task_type, task.day_number)}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      {getDayBadge(task.day_number)}
                      {task.case_client_name && (
                        <span className="font-semibold text-slate-800 text-xs">
                          {task.case_client_name}
                        </span>
                      )}
                      <span className="text-slate-400 text-xs">• Triggered {task.triggered_at}</span>
                    </div>
                    <h3 className="text-base font-bold text-slate-900 mt-0.5">{task.title}</h3>
                  </div>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <NavLink
                    to={`/chaser/${task.case_id}`}
                    className="inline-flex items-center space-x-1 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 px-3 py-1.5 rounded transition"
                  >
                    <span>View Case</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </NavLink>

                  <button
                    onClick={() => setSnoozeModalTask(task)}
                    className="inline-flex items-center space-x-1 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 px-3 py-1.5 rounded transition"
                  >
                    <Moon className="w-3.5 h-3.5 text-slate-500" />
                    <span>Snooze</span>
                  </button>

                  <button
                    onClick={() => completeMutation.mutate(task.id)}
                    disabled={completeMutation.isPending}
                    className="inline-flex items-center space-x-1 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded transition shadow-sm disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Mark Done</span>
                  </button>
                </div>
              </div>

              {/* Pre-drafted text or talking points */}
              {task.pre_drafted_text && (
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-700 font-sans whitespace-pre-wrap leading-relaxed">
                  {task.pre_drafted_text}
                </div>
              )}

              {task.snoozed_until && (
                <div className="text-[11px] text-amber-800 bg-amber-50 border border-amber-200 rounded px-2.5 py-1 inline-flex items-center space-x-1">
                  <Clock className="w-3 h-3 text-amber-600" />
                  <span>Snoozed until <strong>{task.snoozed_until}</strong>: {task.snooze_reason}</span>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-500">
            <CheckSquare className="w-10 h-10 mx-auto text-emerald-500 mb-2" />
            <h3 className="font-bold text-slate-800 text-sm">Inbox Zero: No Reminders Due Today</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
              Use the top bar "Advance Clock" (+3 Days) to simulate time elapsing and see the business day cadence rules fire!
            </p>
          </div>
        )}
      </div>

      {/* Snooze Modal */}
      {snoozeModalTask && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl border border-slate-200 max-w-md w-full p-5">
            <h4 className="font-semibold text-slate-900 text-sm">Snooze Reminder Task</h4>
            <p className="text-xs text-slate-500 mt-1">
              Select business days to postpone and provide a mandatory reason for compliance audit logs.
            </p>

            <div className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700">Postpone By</label>
                <select
                  value={snoozeDays}
                  onChange={(e) => setSnoozeDays(parseInt(e.target.value, 10))}
                  className="mt-1 block w-full text-xs rounded border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                >
                  <option value={1}>1 Business Day</option>
                  <option value={2}>2 Business Days</option>
                  <option value={3}>3 Business Days</option>
                  <option value={5}>5 Business Days (1 Week)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">Reason for Postponement</label>
                <textarea
                  rows={2}
                  value={snoozeReason}
                  onChange={(e) => setSnoozeReason(e.target.value)}
                  className="mt-1 block w-full text-xs rounded border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                  placeholder="e.g. Client stated passport is currently with embassy for visa processing"
                />
              </div>
            </div>

            <div className="mt-5 flex justify-end space-x-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setSnoozeModalTask(null)}
                className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  snoozeMutation.mutate({
                    taskId: snoozeModalTask.id,
                    snooze_days: snoozeDays,
                    reason: snoozeReason,
                  });
                }}
                disabled={snoozeMutation.isPending}
                className="px-3.5 py-1.5 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded shadow-sm disabled:opacity-50"
              >
                {snoozeMutation.isPending ? 'Snoozing...' : 'Confirm Snooze'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
