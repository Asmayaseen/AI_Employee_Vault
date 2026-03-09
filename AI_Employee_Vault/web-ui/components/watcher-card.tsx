"use client";

import { startWatcher, stopWatcher, type WatcherInfo } from "@/lib/api";
import { useState } from "react";

interface WatcherCardProps {
  id: string;
  watcher: WatcherInfo;
  onUpdate: () => void;
}

export default function WatcherCard({ id, watcher, onUpdate }: WatcherCardProps) {
  const [loading, setLoading] = useState(false);

  async function handleToggle() {
    setLoading(true);
    try {
      if (watcher.status === "running") {
        await stopWatcher(id);
      } else {
        await startWatcher(id);
      }
      onUpdate();
    } catch (err) {
      console.error("Watcher toggle failed:", err);
    } finally {
      setLoading(false);
    }
  }

  const isRunning = watcher.status === "running";

  return (
    <div className="card flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-3">
        <div className={`h-3 w-3 rounded-full ${isRunning ? "bg-[#39FF14] animate-pulse shadow-glow-green" : "bg-[#333333] dark:bg-[#333333]"}`} />
        <div>
          <p className="font-medium text-[#0A0A0A] dark:text-[#F0F0F0]">{watcher.name}</p>
          <p className="text-xs text-[#555555] dark:text-[#8899AA]">
            {watcher.script}
            {watcher.pid ? ` (PID: ${watcher.pid})` : ""}
          </p>
        </div>
      </div>
      <button
        onClick={handleToggle}
        disabled={loading}
        className={isRunning ? "btn-danger" : "btn-success"}
      >
        {loading ? "..." : isRunning ? "Stop" : "Start"}
      </button>
    </div>
  );
}
