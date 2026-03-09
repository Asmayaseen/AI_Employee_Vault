"use client";

import { approveFile, rejectFile, type ApprovalItem } from "@/lib/api";
import { useState } from "react";

interface ApprovalCardProps {
  item: ApprovalItem;
  onAction: () => void;
}

export default function ApprovalCard({ item, onAction }: ApprovalCardProps) {
  const [loading, setLoading] = useState<"approve" | "reject" | null>(null);
  const [expanded, setExpanded] = useState(false);

  async function handleApprove() {
    setLoading("approve");
    try {
      await approveFile(item.filename);
      onAction();
    } catch (err) {
      console.error("Approve failed:", err);
    } finally {
      setLoading(null);
    }
  }

  async function handleReject() {
    setLoading("reject");
    try {
      await rejectFile(item.filename);
      onAction();
    } catch (err) {
      console.error("Reject failed:", err);
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="card">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between sm:gap-4">
        <div className="min-w-0 flex-1">
          <p className="font-medium text-[#0A0A0A] dark:text-[#F0F0F0]">
            {item.filename}
          </p>
          <p className="mt-1 text-xs text-[#555555] dark:text-[#8899AA]">
            {new Date(item.created).toLocaleString()} &middot;{" "}
            {(item.size / 1024).toFixed(1)} KB
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleApprove}
            disabled={loading !== null}
            className="btn-success"
          >
            {loading === "approve" ? "..." : "Approve"}
          </button>
          <button
            onClick={handleReject}
            disabled={loading !== null}
            className="btn-danger"
          >
            {loading === "reject" ? "..." : "Reject"}
          </button>
        </div>
      </div>

      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-3 text-xs font-medium text-[#0097A7] hover:text-[#00838F] dark:text-[#00E5FF] dark:hover:text-[#00BCD4]"
      >
        {expanded ? "Hide content" : "Preview content"}
      </button>

      {expanded && (
        <pre className="mt-3 max-h-64 overflow-auto rounded-md bg-[#F5F7FA] p-3 text-xs text-[#555555] dark:bg-[#1A1A1A] dark:text-[#8899AA]">
          {item.content}
        </pre>
      )}
    </div>
  );
}
