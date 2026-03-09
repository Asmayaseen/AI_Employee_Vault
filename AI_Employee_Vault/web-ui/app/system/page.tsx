"use client";

import { useEffect, useState } from "react";
import Header from "@/components/header";
import { getSystemInfo, getHealth, type HealthStatus } from "@/lib/api";

interface SystemInfo {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
}

function UsageBar({ label, percent }: { label: string; percent: number }) {
  const color =
    percent > 90 ? "bg-[#FF2D55]" : percent > 70 ? "bg-[#FF6B00]" : "bg-[#39FF14]";

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm">
        <span className="font-medium text-[#333333] dark:text-[#AABBCC]">{label}</span>
        <span className="text-[#555555] dark:text-[#8899AA]">{percent.toFixed(1)}%</span>
      </div>
      <div className="h-3 w-full overflow-hidden rounded-full bg-[#E0E0E0] dark:bg-[#1A1A1A]">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${Math.min(percent, 100)}%` }} />
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    healthy: "badge-green",
    active: "badge-green",
    running: "badge-green",
    degraded: "badge-yellow",
    warning: "badge-yellow",
    unhealthy: "badge-red",
    unavailable: "badge-red",
    stopped: "badge-red",
  };
  return <span className={styles[status] || "badge-blue"}>{status}</span>;
}

function PlatinumInfoCard({ title, items }: { title: string; items: { label: string; value: string; status?: string }[] }) {
  return (
    <div>
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-[#555555] dark:text-[#8899AA]">
        {title}
      </h3>
      <div className="card space-y-3">
        {items.map((item) => (
          <div key={item.label} className="flex items-center justify-between">
            <span className="text-sm text-[#333333] dark:text-[#AABBCC]">{item.label}</span>
            <div className="flex items-center gap-2">
              {item.status && (
                <div className={`h-2 w-2 rounded-full ${
                  item.status === "active" ? "bg-[#39FF14]" :
                  item.status === "synced" ? "bg-[#39FF14]" :
                  item.status === "warning" ? "bg-[#FF6B00]" :
                  "bg-[#555555]"
                }`} />
              )}
              <span className="text-sm font-medium text-[#555555] dark:text-[#8899AA]">{item.value}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function SystemPage() {
  const [system, setSystem] = useState<SystemInfo | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function fetchData() {
    try {
      const [s, h] = await Promise.all([getSystemInfo(), getHealth()]);
      setSystem(s);
      setHealth(h);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch");
    }
  }

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <Header title="System Health" />
      <div className="p-4 sm:p-6">
        {error && (
          <div className="mb-4 card border-red-200 bg-red-50 text-red-800 dark:border-[#FF2D5540] dark:bg-[#FF2D5510] dark:text-[#FF2D55]">
            <p>{error}</p>
          </div>
        )}

        {!system || !health ? (
          <div className="flex items-center justify-center p-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#0097A7] border-t-transparent dark:border-[#00E5FF] dark:border-t-transparent" />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Resource Usage */}
            <div>
              <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-[#555555] dark:text-[#8899AA]">
                Resource Usage
              </h3>
              <div className="card space-y-4">
                <UsageBar label="CPU" percent={system.cpu_percent} />
                <UsageBar label="Memory" percent={system.memory_percent} />
                <UsageBar label="Disk" percent={system.disk_percent} />
              </div>
            </div>

            {/* Overall Health */}
            <div>
              <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-[#555555] dark:text-[#8899AA]">
                Overall Status
              </h3>
              <div className="card">
                <div className="mb-4 flex items-center gap-3">
                  <div
                    className={`h-4 w-4 rounded-full ${
                      health.status === "healthy"
                        ? "bg-[#39FF14] shadow-glow-green"
                        : health.status === "degraded"
                        ? "bg-[#FF6B00]"
                        : "bg-[#FF2D55]"
                    }`}
                  />
                  <span className="text-lg font-semibold capitalize text-[#0A0A0A] dark:text-[#F0F0F0]">
                    {health.status}
                  </span>
                  <span className="ml-auto rounded-full bg-[#7C4DFF20] px-3 py-0.5 text-xs font-semibold text-[#7C4DFF] dark:bg-[#B388FF20] dark:text-[#B388FF]">
                    Platinum
                  </span>
                </div>
                <p className="text-xs text-[#555555] dark:text-[#8899AA]">
                  Last checked: {new Date(health.timestamp).toLocaleString()}
                </p>
              </div>
            </div>

            {/* Platinum: Cloud Status */}
            <PlatinumInfoCard
              title="Cloud Status"
              items={[
                { label: "Cloud Agent", value: "Ready", status: "active" },
                { label: "Local Agent", value: "Active", status: "active" },
                { label: "Deployment", value: "Configured" },
                { label: "SSL", value: "Pending setup" },
              ]}
            />

            {/* Platinum: Vault Sync */}
            <PlatinumInfoCard
              title="Vault Sync"
              items={[
                { label: "Sync Status", value: "Local only", status: "warning" },
                { label: "Last Sync", value: "Not configured" },
                { label: "Strategy", value: "Git (local wins)" },
                { label: "Interval", value: "5 minutes" },
              ]}
            />

            {/* Platinum: Work Zones */}
            <PlatinumInfoCard
              title="Work Zones"
              items={[
                { label: "Active Zone", value: "Local", status: "active" },
                { label: "Auto Failover", value: "Enabled" },
                { label: "Failover Threshold", value: "3 failures" },
                { label: "Cloud Zone", value: "Not deployed" },
              ]}
            />

            {/* Platinum: Health Monitor */}
            <PlatinumInfoCard
              title="Health Monitor"
              items={[
                { label: "Monitor Status", value: "Available", status: "active" },
                { label: "Check Interval", value: "30 seconds" },
                { label: "Alert Channels", value: "Email" },
                { label: "Alerts Enabled", value: "Configure env" },
              ]}
            />

            {/* Service Details */}
            <div className="lg:col-span-2">
              <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-[#555555] dark:text-[#8899AA]">
                Services
              </h3>
              <div className="card overflow-x-auto">
                <table className="w-full min-w-[500px] text-sm">
                  <thead>
                    <tr className="border-b border-[#0097A71A] dark:border-[#00E5FF1A]">
                      <th className="px-4 py-3 text-left font-medium text-[#555555] dark:text-[#8899AA]">
                        Service
                      </th>
                      <th className="px-4 py-3 text-left font-medium text-[#555555] dark:text-[#8899AA]">
                        Status
                      </th>
                      <th className="px-4 py-3 text-left font-medium text-[#555555] dark:text-[#8899AA]">
                        Details
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(health.services).map(([name, service]) => (
                      <tr key={name} className="border-b border-[#0097A710] last:border-0 dark:border-[#00E5FF10]">
                        <td className="px-4 py-3 font-medium capitalize text-[#0A0A0A] dark:text-[#F0F0F0]">
                          {name.replace(/_/g, " ")}
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge status={service.status} />
                        </td>
                        <td className="px-4 py-3 text-[#555555] dark:text-[#8899AA]">
                          {Object.entries(service)
                            .filter(([k]) => k !== "status")
                            .map(([k, v]) => `${k}: ${v}`)
                            .join(", ") || "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
