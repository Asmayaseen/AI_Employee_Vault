import type { ActionItem as ActionItemType } from "@/lib/api";

const priorityColors: Record<string, string> = {
  high: "badge-red",
  medium: "badge-yellow",
  low: "badge-blue",
};

const typeIcons: Record<string, string> = {
  email: "M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z",
  linkedin: "M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z",
  whatsapp: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z",
  file: "M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z",
};

export default function ActionItemCard({ action }: { action: ActionItemType }) {
  const icon = typeIcons[action.type] || typeIcons.file;

  return (
    <div className="card flex items-start gap-3">
      <svg className="mt-0.5 h-5 w-5 flex-shrink-0 text-[#8899AA]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
      </svg>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <p className="truncate font-medium text-[#0A0A0A] dark:text-[#F0F0F0]">
            {action.title}
          </p>
          <span className={priorityColors[action.priority] || "badge-blue"}>
            {action.priority}
          </span>
        </div>
        <p className="mt-0.5 text-xs text-[#555555] dark:text-[#8899AA]">
          {action.source} &middot; {new Date(action.created).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
