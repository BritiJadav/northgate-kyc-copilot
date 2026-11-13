import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  FileSearch,
  Users,
  CheckSquare,
  ShieldCheck,
  BarChart3,
  Terminal,
  Calendar,
  FastForward,
  UserCheck,
  RefreshCw,
  Cpu
} from 'lucide-react';
import { UserRole } from '../types';

interface NavbarProps {
  currentRole: UserRole;
  onRoleChange: (role: UserRole) => void;
  simulatedDate: string;
  onAdvanceClock: (days: number) => void;
  onResetDemo: () => void;
  onOpenTrace: () => void;
  agentRunsCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentRole,
  onRoleChange,
  simulatedDate,
  onAdvanceClock,
  onResetDemo,
  onOpenTrace,
  agentRunsCount,
}) => {
  const [advancing, setAdvancing] = useState(false);

  const handleAdvance = async (days: number) => {
    setAdvancing(true);
    try {
      await onAdvanceClock(days);
    } finally {
      setAdvancing(false);
    }
  };

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-6">
            <NavLink to="/" className="flex items-center space-x-2.5 font-bold text-base tracking-tight hover:opacity-90">
              <div className="w-8 h-8 rounded-md bg-blue-600 flex items-center justify-center font-bold text-white shadow-sm">
                N
              </div>
              <div className="flex flex-col">
                <span className="leading-tight text-white font-semibold">Northgate</span>
                <span className="text-[10px] text-blue-400 uppercase tracking-widest font-mono">KYC Copilot</span>
              </div>
            </NavLink>

            {/* Navigation Links */}
            <nav className="hidden md:flex items-center space-x-1 text-sm font-medium">
              <NavLink
                to="/"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md transition ${isActive ? 'bg-slate-800 text-white font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-800/60'}`
                }
              >
                Overview
              </NavLink>

              <NavLink
                to="/chaser"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition ${isActive ? 'bg-blue-600 text-white font-semibold shadow-sm' : 'text-slate-300 hover:text-white hover:bg-slate-800/60'}`
                }
              >
                <FileSearch className="w-4 h-4" />
                <span>Document Chaser</span>
              </NavLink>

              <NavLink
                to="/tasks"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition ${isActive ? 'bg-slate-800 text-white font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-800/60'}`
                }
              >
                <CheckSquare className="w-4 h-4" />
                <span>RM Tasks</span>
              </NavLink>

              <NavLink
                to="/analyst"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition ${isActive ? 'bg-indigo-600 text-white font-semibold shadow-sm' : 'text-slate-300 hover:text-white hover:bg-slate-800/60'}`
                }
              >
                <Users className="w-4 h-4" />
                <span>Analyst Assist</span>
              </NavLink>

              <NavLink
                to="/metrics"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition ${isActive ? 'bg-slate-800 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800/60'}`
                }
              >
                <BarChart3 className="w-4 h-4" />
                <span>Metrics</span>
              </NavLink>

              <NavLink
                to="/governance"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition ${isActive ? 'bg-slate-800 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800/60'}`
                }
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Governance</span>
              </NavLink>

              <NavLink
                to="/eval"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition ${isActive ? 'bg-slate-800 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800/60'}`
                }
              >
                <Cpu className="w-4 h-4" />
                <span>Eval</span>
              </NavLink>
            </nav>
          </div>

          {/* Right Controls: Role, Clock, Trace Drawer */}
          <div className="flex items-center space-x-3 text-xs">
            {/* Role Switcher */}
            <div className="flex items-center space-x-1.5 bg-slate-800 border border-slate-700 rounded-md px-2.5 py-1">
              <UserCheck className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-slate-400">Role:</span>
              <select
                value={currentRole}
                onChange={(e) => onRoleChange(e.target.value as UserRole)}
                className="bg-transparent font-medium text-white focus:outline-none cursor-pointer"
              >
                <option value="RM" className="bg-slate-800 text-white">Relationship Mgr</option>
                <option value="Analyst" className="bg-slate-800 text-white">KYC Analyst</option>
                <option value="MLRO" className="bg-slate-800 text-white">MLRO</option>
                <option value="Ops" className="bg-slate-800 text-white">Operations</option>
              </select>
            </div>

            {/* Advance Clock Controls */}
            <div className="flex items-center space-x-1 bg-slate-800/80 border border-slate-700/80 rounded-md p-0.5">
              <span className="text-[11px] text-slate-300 px-2 font-mono flex items-center space-x-1">
                <Calendar className="w-3 h-3 text-amber-400" />
                <span>{simulatedDate}</span>
              </span>
              <button
                onClick={() => handleAdvance(1)}
                disabled={advancing}
                title="Advance mock clock by 1 business day"
                className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-700 hover:bg-slate-600 text-amber-300 transition flex items-center space-x-1 disabled:opacity-50"
              >
                <FastForward className="w-3 h-3" />
                <span>+1 Day</span>
              </button>
              <button
                onClick={() => handleAdvance(3)}
                disabled={advancing}
                title="Advance mock clock by 3 business days (triggers cadence rules)"
                className="px-2 py-0.5 rounded text-[11px] font-medium bg-amber-600/30 hover:bg-amber-600/50 text-amber-200 border border-amber-500/30 transition flex items-center space-x-1 disabled:opacity-50"
              >
                <span>+3 Days</span>
              </button>
            </div>

            {/* Trace Drawer Trigger */}
            <button
              onClick={onOpenTrace}
              className="flex items-center space-x-1.5 bg-blue-950/60 hover:bg-blue-900 border border-blue-700/50 text-blue-200 px-2.5 py-1 rounded-md transition"
              title="Open step-by-step agent execution trace drawer"
            >
              <Cpu className="w-3.5 h-3.5 text-blue-400" />
              <span>Agent Trace</span>
              {agentRunsCount > 0 && (
                <span className="bg-blue-600 text-white font-mono text-[10px] px-1.5 py-0.2 rounded-full">
                  {agentRunsCount}
                </span>
              )}
            </button>

            {/* Reset Demo */}
            <button
              onClick={onResetDemo}
              className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition"
              title="Reset demo data to initial state"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
