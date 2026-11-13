import React from 'react';
import { Mail, CheckCircle2, AlertCircle, Clock, Calendar } from 'lucide-react';
import { ChaseEmail, ReminderTask, ReceivedDocument } from '../types';

interface TimelineProps {
  emails: ChaseEmail[];
  reminders: ReminderTask[];
  documents: ReceivedDocument[];
  lastContactDate?: string | null;
}

export const Timeline: React.FC<TimelineProps> = ({ emails, reminders, documents, lastContactDate }) => {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 shadow-sm">
      <h4 className="text-xs font-semibold text-slate-900 mb-3 flex items-center space-x-1.5 uppercase tracking-wider">
        <Calendar className="w-3.5 h-3.5 text-blue-600" />
        <span>Case Activity & Contact Timeline</span>
      </h4>

      <div className="flex flex-wrap items-center gap-3 text-xs">
        {lastContactDate && (
          <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded-md px-3 py-1.5">
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <div>
              <span className="text-slate-500 text-[10px] block">Last Contact Date</span>
              <strong className="text-slate-800">{lastContactDate}</strong>
            </div>
          </div>
        )}

        <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded-md px-3 py-1.5">
          <Mail className="w-3.5 h-3.5 text-blue-500" />
          <div>
            <span className="text-slate-500 text-[10px] block">Emails Sent (Simulated)</span>
            <strong className="text-slate-800">
              {emails.filter(e => e.status === 'sent_simulated').length} / {emails.length} drafted
            </strong>
          </div>
        </div>

        <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded-md px-3 py-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
          <div>
            <span className="text-slate-500 text-[10px] block">Documents Received</span>
            <strong className="text-slate-800">{documents.length} files</strong>
          </div>
        </div>

        <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 rounded-md px-3 py-1.5">
          <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
          <div>
            <span className="text-slate-500 text-[10px] block">Reminder Cadence Tasks</span>
            <strong className="text-slate-800">{reminders.length} tasks generated</strong>
          </div>
        </div>
      </div>
    </div>
  );
};
