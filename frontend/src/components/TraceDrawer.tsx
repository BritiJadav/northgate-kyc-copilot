import React from 'react';
import { X, Cpu, Clock, Hash, CheckCircle2, AlertCircle, Database } from 'lucide-react';
import { AgentRun } from '../types';

interface TraceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  runs: AgentRun[];
}

export const TraceDrawer: React.FC<TraceDrawerProps> = ({ isOpen, onClose, runs }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" onClick={onClose} />

      <div className="fixed inset-y-0 right-0 pl-10 max-w-full flex">
        <div className="w-screen max-w-xl bg-white shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <Cpu className="w-5 h-5 text-blue-400" />
              <div>
                <h2 className="text-base font-semibold">Agent Execution Trace Drawer</h2>
                <p className="text-xs text-slate-400">Step-by-step LLM and engine telemetry log</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Trace List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50">
            {runs.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-sm">
                No agent runs recorded in this session yet.
              </div>
            ) : (
              runs.map((run) => (
                <div
                  key={run.id}
                  className="bg-white rounded-lg border border-slate-200 p-3.5 shadow-sm hover:border-blue-400 transition"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm text-slate-900 flex items-center space-x-1.5">
                      <span className="h-2 w-2 rounded-full bg-blue-600" />
                      <span>{run.agent_name}</span>
                    </span>
                    <span className="text-[11px] font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                      v{run.prompt_version}
                    </span>
                  </div>

                  <div className="mt-2.5 grid grid-cols-2 gap-2 text-xs text-slate-600">
                    <div className="flex items-center space-x-1">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      <span>Latency: <strong className="text-slate-800">{run.latency_ms} ms</strong></span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Cpu className="w-3.5 h-3.5 text-slate-400" />
                      <span>Tokens: <strong className="text-slate-800">{run.tokens_used}</strong></span>
                    </div>
                  </div>

                  <div className="mt-2.5 flex items-center justify-between pt-2 border-t border-slate-100 text-[11px]">
                    <div className="flex items-center space-x-1 text-slate-500 font-mono truncate max-w-[240px]">
                      <Hash className="w-3 h-3 text-slate-400" />
                      <span className="truncate">{run.input_hash}</span>
                    </div>
                    {run.cache_hit ? (
                      <span className="inline-flex items-center space-x-1 text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded font-medium">
                        <Database className="w-3 h-3 text-emerald-600" />
                        <span>Cache Hit (C12)</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded font-medium">
                        <CheckCircle2 className="w-3 h-3 text-blue-600" />
                        <span>Live Model</span>
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
