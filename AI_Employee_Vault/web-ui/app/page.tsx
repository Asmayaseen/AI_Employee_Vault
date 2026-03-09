"use client";

import { useEffect, useState } from "react";
import Header from "@/components/header";
import StatCard from "@/components/stat-card";
import WatcherCard from "@/components/watcher-card";
import ActionItemCard from "@/components/action-item";
import LogEntryRow from "@/components/log-entry";
import { getStatus, getLogs, type SystemStatus, type LogEntry } from "@/lib/api";

export default function DashboardPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function fetchData() {
    try {
      const [s, l] = await Promise.all([getStatus(), getLogs()]);
      setStatus(s);
      setLogs(l.logs);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch data");
    }
  }

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <>
        <Header title="Dashboard" />
        <div className="p-6">
          <div className="card border-red-200 bg-red-50 text-red-800 dark:border-[#FF2D5540] dark:bg-[#FF2D5510] dark:text-[#FF2D55]">
            <p className="font-medium">Connection Error</p>
            <p className="mt-1 text-sm">{error}</p>
            <p className="mt-2 text-xs">Make sure the Flask backend is running on port 9000.</p>
          </div>
        </div>
      </>
    );
  }

  if (!status) {
    return (
      <>
        <Header title="Dashboard" />
        <div className="flex items-center justify-center p-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#0097A7] border-t-transparent dark:border-[#00E5FF] dark:border-t-transparent" />
        </div>
      </>
    );
  }

  const watcherEntries = Object.entries(status.watchers);
  const runningCount = watcherEntries.filter(([, w]) => w.status === "running").length;

  return (
    <>
      <Header title="Dashboard" />
      <div className="space-y-6 p-4 sm:p-6">
        {/* Stats Row */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Pending Actions"
            value={status.statistics.total_actions}
            icon="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            color="amber"
          />
          <StatCard
            label="Emails Processed"
            value={status.statistics.processed_emails}
            icon="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            color="blue"
          />
          <StatCard
            label="Watchers Running"
            value={`${runningCount}/${watcherEntries.length}`}
            icon="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
            color="green"
          />
          <StatCard
            label="Logs Today"
            value={status.statistics.logs_today}
            icon="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            color="purple"
          />
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Watcher Status */}
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[#555555] dark:text-[#8899AA]">
              Watchers
            </h3>
            <div className="space-y-2">
              {watcherEntries.map(([id, watcher]) => (
                <WatcherCard key={id} id={id} watcher={watcher} onUpdate={fetchData} />
              ))}
            </div>
          </div>

          {/* Pending Actions */}
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[#555555] dark:text-[#8899AA]">
              Pending Actions ({status.pending_actions.length})
            </h3>
            <div className="space-y-2">
              {status.pending_actions.length === 0 ? (
                <div className="card text-center text-sm text-[#555555] dark:text-[#8899AA]">
                  No pending actions
                </div>
              ) : (
                status.pending_actions.slice(0, 10).map((action) => (
                  <ActionItemCard key={action.filename} action={action} />
                ))
              )}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[#555555] dark:text-[#8899AA]">
            Recent Activity
          </h3>
          <div className="card">
            {logs.length === 0 ? (
              <p className="text-center text-sm text-[#555555] dark:text-[#8899AA]">
                No log entries today
              </p>
            ) : (
              logs.slice(-15).reverse().map((log, i) => (
                <LogEntryRow key={i} log={log} />
              ))
            )}
          </div>
        </div>
      </div>
    </>
  );
}
