import type { LogEntry as LogEntryType } from "@/lib/api";

export default function LogEntryRow({ log }: { log: LogEntryType }) {
  return (
    <div className="flex items-start gap-3 border-b border-[#0097A71A] py-2.5 last:border-0 dark:border-[#00E5FF1A]">
      <div className="mt-1 h-2 w-2 flex-shrink-0 rounded-full bg-[#0097A7] dark:bg-[#00E5FF]" />
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          {log.action_type && (
            <span className="badge-blue">{log.action_type}</span>
          )}
          {log.source && (
            <span className="text-xs text-[#555555] dark:text-[#8899AA]">
              {log.source}
            </span>
          )}
        </div>
        <p className="mt-0.5 text-sm text-[#333333] dark:text-[#AABBCC]">
          {log.details || JSON.stringify(log)}
        </p>
        {log.timestamp && (
          <p className="mt-0.5 text-xs text-[#888888] dark:text-[#667788]">
            {new Date(log.timestamp).toLocaleString()}
          </p>
        )}
      </div>
    </div>
  );
}
