"use client";

import { useEffect, useState } from "react";
import Header from "@/components/header";
import ApprovalCard from "@/components/approval-card";
import { getApprovals, type ApprovalItem } from "@/lib/api";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function fetchApprovals() {
    try {
      const data = await getApprovals();
      setApprovals(data.approvals);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch approvals");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <Header title="Approvals" />
      <div className="p-4 sm:p-6">
        {error && (
          <div className="mb-4 card border-red-200 bg-red-50 text-red-800 dark:border-[#FF2D5540] dark:bg-[#FF2D5510] dark:text-[#FF2D55]">
            <p>{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#0097A7] border-t-transparent dark:border-[#00E5FF] dark:border-t-transparent" />
          </div>
        ) : approvals.length === 0 ? (
          <div className="card text-center">
            <svg className="mx-auto h-12 w-12 text-[#0097A740] dark:text-[#00E5FF30]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="mt-3 text-sm font-medium text-[#0A0A0A] dark:text-[#F0F0F0]">All caught up</p>
            <p className="mt-1 text-sm text-[#555555] dark:text-[#8899AA]">
              No items pending approval.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-[#555555] dark:text-[#8899AA]">
              {approvals.length} item{approvals.length !== 1 ? "s" : ""} pending approval
            </p>
            {approvals.map((item) => (
              <ApprovalCard key={item.filename} item={item} onAction={fetchApprovals} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
