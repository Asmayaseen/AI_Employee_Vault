"use client";

import { useEffect, useState } from "react";
import Header from "@/components/header";
import LogEntryRow from "@/components/log-entry";
import { getLogsByDate, type LogEntry } from "@/lib/api";

export default function LogsPage() {
  const today = new Date().toISOString().split("T")[0];
  const [date, setDate] = useState(today);
  const [actionType, setActionType] = useState("");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  async function fetchLogs() {
    setLoading(true);
    try {
      const data = await getLogsByDate(date, actionType || undefined);
      setLogs(data.logs);
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchLogs();
  }, [date, actionType]);

  function exportLogs() {
    const blob = new Blob([JSON.stringify(logs, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `logs-${date}${actionType ? `-${actionType}` : ""}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <>
      <Header title="Logs" />
      <div className="p-4 sm:p-6">
        {/* Filters */}
        <div className="mb-6 flex flex-wrap items-center gap-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-[#555555] dark:text-[#8899AA]">
              Date
            </label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="rounded-md border border-[#0097A730] bg-white px-3 py-2 text-sm focus:border-[#0097A7] focus:outline-none focus:ring-1 focus:ring-[#0097A7] dark:border-[#00E5FF30] dark:bg-[#1A1A1A] dark:text-[#F0F0F0] dark:focus:border-[#00E5FF] dark:focus:ring-[#00E5FF]"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-[#555555] dark:text-[#8899AA]">
              Action Type
            </label>
            <input
              type="text"
              value={actionType}
              onChange={(e) => setActionType(e.target.value)}
              placeholder="e.g. email_processed"
              className="rounded-md border border-[#0097A730] bg-white px-3 py-2 text-sm focus:border-[#0097A7] focus:outline-none focus:ring-1 focus:ring-[#0097A7] dark:border-[#00E5FF30] dark:bg-[#1A1A1A] dark:text-[#F0F0F0] dark:focus:border-[#00E5FF] dark:focus:ring-[#00E5FF]"
            />
          </div>
          <div className="self-end">
            <button onClick={exportLogs} className="btn-secondary" disabled={logs.length === 0}>
              Export JSON
            </button>
          </div>
        </div>

        {/* Log Count */}
        <p className="mb-4 text-sm text-[#555555] dark:text-[#8899AA]">
          {loading ? "Loading..." : `${logs.length} log entries`}
        </p>

        {/* Log Entries */}
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#0097A7] border-t-transparent dark:border-[#00E5FF] dark:border-t-transparent" />
          </div>
        ) : logs.length === 0 ? (
          <div className="card text-center">
            <p className="text-sm text-[#555555] dark:text-[#8899AA]">
              No log entries for {date}
              {actionType ? ` with type "${actionType}"` : ""}
            </p>
          </div>
        ) : (
          <div className="card">
            {logs.map((log, i) => (
              <LogEntryRow key={i} log={log} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
