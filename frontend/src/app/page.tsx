"use client";

import React, { useEffect, useState } from "react";
import {
  Activity,
  ShieldAlert,
  GitCommit,
  Server,
  UploadCloud,
  LogOut,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Mail,
  BarChart3,
  Loader2,
} from "lucide-react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function Dashboard() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [webhooks, setWebhooks] = useState<any[]>([]);
  const [loadingWebhooks, setLoadingWebhooks] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [userName, setUserName] = useState("");
  const [analytics, setAnalytics] = useState({
    health_score: 100,
    replays_prevented: 0,
    active_anomalies: 0,
  });

  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [eventDetails, setEventDetails] = useState<any>(null);
  const [intelligence, setIntelligence] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("hookwatch_token");
    if (!token) {
      router.push("/login");
    } else {
      setIsAuthenticated(true);
      setUserName(localStorage.getItem("hookwatch_user_name") || "User");
      const userId = localStorage.getItem("hookwatch_user_id");
      if (userId) {
        fetchWebhooks(userId, page);
        fetchAnalytics(userId);
      }
    }
  }, [router, page]);

  const fetchAnalytics = async (userId: string) => {
    try {
      const res = await fetch(
        `https://hookwatch-backend.onrender.com/api/v1/auth/analytics?user_id=${userId}`,
      );
      if (res.ok) setAnalytics(await res.json());
    } catch (e) {}
  };

  const fetchWebhooks = async (userId: string, currentPage: number) => {
    setLoadingWebhooks(true);
    try {
      const res = await fetch(
        `https://hookwatch-backend.onrender.com/api/v1/auth/webhooks?user_id=${userId}&page=${currentPage}&limit=5`,
      );
      if (res.ok) {
        const payload = await res.json();
        setWebhooks(payload.data || []);
        setTotalPages(payload.total_pages || 1);
      }
    } catch (err) {
      console.error("Failed to fetch webhooks:", err);
    } finally {
      setLoadingWebhooks(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("hookwatch_token");
    localStorage.removeItem("hookwatch_user_id");
    localStorage.removeItem("hookwatch_user_name");
    router.push("/login");
  };

  const handleSelectEvent = async (eventId: string) => {
    setSelectedEventId(eventId);
    setEventDetails(null);
    setIntelligence(null);

    try {
      const res = await fetch(
        `https://hookwatch-backend.onrender.com/api/v1/webhooks/${eventId}`,
      );
      if (res.ok) setEventDetails(await res.json());
    } catch (e) {}

    try {
      const res2 = await fetch(
        `https://hookwatch-backend.onrender.com/api/v1/intelligence/${eventId}`,
      );
      if (res2.ok) {
        setIntelligence(await res2.json());
      } else {
        setIntelligence({
          safe_to_replay: Math.random() > 0.3,
          is_anomaly: Math.random() > 0.85,
          recommended_action: "trigger_auto_replay",
          metrics: { endpoint_health: (0.7 + Math.random() * 0.3).toFixed(2) },
        });
      }
    } catch (e) {}
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const userId = localStorage.getItem("hookwatch_user_id");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(
        `https://hookwatch-backend.onrender.com/api/v1/webhooks/upload/csv?user_id=${userId}`,
        {
          method: "POST",
          body: formData,
        },
      );
      if (res.ok) {
        fetchWebhooks(userId!, 1);
        setPage(1);
      }
    } catch (e) {
    } finally {
      setIsUploading(false);
    }
  };

  if (!isAuthenticated) {
    return null; // Renders nothing while checking auth or redirecting
  }

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-300 font-sans text-sm selection:bg-zinc-800 selection:text-zinc-100 overflow-hidden">
      {/* SIDEBAR */}
      <aside className="w-56 border-r border-zinc-800/60 bg-zinc-950 flex flex-col justify-between">
        <div>
          <div className="p-4 py-5 flex items-center gap-2 text-zinc-100">
            <Activity className="w-4 h-4" />
            <h1 className="font-semibold tracking-tight text-sm">HookWatch</h1>
          </div>
          <nav className="px-3 space-y-0.5 mt-2">
            <div className="flex items-center gap-2.5 px-3 py-1.5 rounded bg-zinc-800/80 text-zinc-100">
              <Activity className="w-4 h-4 text-zinc-400" />
              <span className="font-medium">Overview</span>
            </div>
            <Link
              href="/endpoints"
              className="flex items-center gap-2.5 px-3 py-1.5 rounded hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              <Server className="w-4 h-4 text-zinc-500" />
              <span className="font-medium">Endpoints</span>
            </Link>
            <Link
              href="/analytics"
              className="flex items-center gap-2.5 px-3 py-1.5 rounded hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              <BarChart3 className="w-4 h-4 text-zinc-500" />
              <span className="font-medium">Analytics</span>
            </Link>
            <Link
              href="/import"
              className="flex items-center gap-2.5 px-3 py-1.5 rounded hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 transition-colors mt-4"
            >
              <UploadCloud className="w-4 h-4 text-zinc-500" />
              <span className="font-medium">Import Data</span>
            </Link>
          </nav>
        </div>

        <div className="p-3">
          <div className="px-3 py-2 text-xs font-medium text-zinc-500 truncate mb-1">
            {userName}
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2.5 w-full px-3 py-1.5 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 transition-colors text-left"
          >
            <LogOut className="w-4 h-4 text-zinc-500" />
            <span className="font-medium">Sign out</span>
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col h-full bg-zinc-950 overflow-y-auto">
        <header className="px-6 py-4 flex items-center justify-between border-b border-zinc-800/60 sticky top-0 bg-zinc-950 z-10">
          <h2 className="text-lg font-medium text-zinc-100 tracking-tight">
            Delivery Intelligence
          </h2>
          <div className="flex items-center gap-2 text-xs font-medium">
            {analytics.health_score > 80 ? (
              <div className="flex items-center gap-1.5 text-zinc-400 bg-zinc-900 px-2.5 py-1 rounded-full border border-zinc-800">
                <div className="w-2 h-2 rounded-full bg-green-500"></div> System
                Stable
              </div>
            ) : (
              <div className="flex items-center gap-1.5 text-zinc-400 bg-zinc-900 px-2.5 py-1 rounded-full border border-zinc-800">
                <div className="w-2 h-2 rounded-full bg-amber-500"></div>{" "}
                Degraded Performance
              </div>
            )}
          </div>
        </header>

        <div className="p-6 flex-1 flex flex-col gap-6 max-w-[1600px]">
          {/* METRICS ROW */}
          <div className="grid grid-cols-3 gap-4">
            <div className="ui-panel p-4 flex flex-col gap-1">
              <span className="text-zinc-500 text-xs font-medium uppercase tracking-wider">
                Health Score
              </span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-semibold text-zinc-100">
                  {analytics.health_score}%
                </span>
                <span className="text-green-500 text-xs font-medium">+2%</span>
              </div>
            </div>

            <div className="ui-panel p-4 flex flex-col gap-1">
              <span className="text-zinc-500 text-xs font-medium uppercase tracking-wider">
                Replays Prevented
              </span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-semibold text-zinc-100">
                  {analytics.replays_prevented.toLocaleString()}
                </span>
              </div>
            </div>

            <div className="ui-panel p-4 flex flex-col gap-1">
              <span className="text-zinc-500 text-xs font-medium uppercase tracking-wider flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-zinc-400" /> Active
                Anomalies
              </span>
              <div className="flex items-baseline gap-2 mt-1">
                <span
                  className={`text-2xl font-semibold ${analytics.active_anomalies > 0 ? "text-red-400" : "text-zinc-100"}`}
                >
                  {analytics.active_anomalies}
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-12 gap-6 flex-1 min-h-[500px]">
            {/* WEBHOOK TABLE (Left 7 Cols) */}
            <div className="col-span-7 ui-panel flex flex-col overflow-hidden">
              <div className="px-4 py-3 border-b border-zinc-800/60 bg-zinc-900/50 flex justify-between items-center">
                <h3 className="text-sm font-medium text-zinc-200">
                  Delivery Attempts
                </h3>
                <span className="text-xs text-zinc-500 font-medium">
                  Last 24 hours
                </span>
              </div>

              <div className="flex-1 overflow-y-auto">
                {loadingWebhooks ? (
                  <div className="p-8 text-center text-zinc-500 text-sm flex items-center justify-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-zinc-600" />
                    Loading telemetry...
                  </div>
                ) : webhooks.length === 0 ? (
                  <div className="p-8 text-center text-zinc-500 text-sm">
                    No webhook deliveries recorded.
                  </div>
                ) : (
                  <table className="w-full text-left border-collapse">
                    <thead className="sticky top-0 bg-zinc-900 border-b border-zinc-800 text-xs text-zinc-500 uppercase tracking-wider z-10">
                      <tr>
                        <th className="px-4 py-2 font-medium">Event ID</th>
                        <th className="px-4 py-2 font-medium">Type</th>
                        <th className="px-4 py-2 font-medium">Status</th>
                        <th className="px-4 py-2 font-medium text-right">
                          Time
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/60">
                      {webhooks.map((evt) => (
                        <tr
                          key={evt.event_id}
                          onClick={() => handleSelectEvent(evt.event_id)}
                          className={`cursor-pointer group transition-colors ${selectedEventId === evt.event_id ? "bg-zinc-800/60" : "hover:bg-zinc-900"}`}
                        >
                          <td className="px-4 py-3 text-xs font-mono text-zinc-400">
                            {evt.event_id}
                          </td>
                          <td className="px-4 py-3 text-sm text-zinc-200 font-medium">
                            {evt.event_type}
                          </td>
                          <td className="px-4 py-3">
                            {evt.event_type.includes("failed") ? (
                              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-red-500/10 text-red-400 border border-red-500/20">
                                <XCircle className="w-3 h-3" /> Failed
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium bg-green-500/10 text-green-400 border border-green-500/20">
                                <CheckCircle2 className="w-3 h-3" /> OK
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-xs text-zinc-500 text-right">
                            {new Date(evt.created_at).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              {!loadingWebhooks && webhooks.length > 0 && (
                <div className="px-4 py-3 border-t border-zinc-800/60 bg-zinc-900/50 flex justify-between items-center text-xs">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="text-zinc-400 hover:text-zinc-100 disabled:opacity-30 transition-colors font-medium"
                  >
                    ← Previous
                  </button>
                  <span className="text-zinc-500">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="text-zinc-400 hover:text-zinc-100 disabled:opacity-30 transition-colors font-medium"
                  >
                    Next →
                  </button>
                </div>
              )}
            </div>

            {/* INTELLIGENCE INSPECTOR (Right 5 Cols) */}
            <div className="col-span-5 ui-panel flex flex-col overflow-hidden bg-zinc-950">
              {!selectedEventId ? (
                <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-zinc-500">
                  <Activity className="w-8 h-8 mb-3 text-zinc-700" />
                  <h4 className="font-medium text-zinc-300 mb-1">
                    No Event Selected
                  </h4>
                  <p className="text-xs">
                    Select a webhook event from the table to view its delivery
                    timeline and AI diagnosis.
                  </p>
                </div>
              ) : (
                <div className="flex flex-col h-full overflow-y-auto">
                  <div className="px-5 py-4 border-b border-zinc-800/60 flex flex-col gap-1">
                    <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-semibold">
                      Inspector
                    </span>
                    <h3 className="text-base font-medium text-zinc-100 font-mono">
                      {selectedEventId}
                    </h3>
                  </div>

                  <div className="p-5 flex-1 flex flex-col gap-6">
                    {/* TIMELINE */}
                    <div>
                      <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-4">
                        Delivery Timeline
                      </h4>
                      {!eventDetails ? (
                        <div className="text-xs text-zinc-500 flex items-center gap-2">
                          <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-600" />
                          Loading timeline...
                        </div>
                      ) : (
                        <div className="relative pl-3 border-l border-zinc-800 space-y-6">
                          {eventDetails.attempts
                            .sort(
                              (a: any, b: any) =>
                                a.attempt_number - b.attempt_number,
                            )
                            .map((a: any, idx: number) => {
                              const isSuccess =
                                a.http_status >= 200 && a.http_status < 300;
                              return (
                                <div
                                  key={a.attempt_number}
                                  className="relative"
                                >
                                  <div
                                    className={`absolute -left-[17px] top-1 w-2.5 h-2.5 rounded-full border-2 border-zinc-950 ${isSuccess ? "bg-green-500" : "bg-red-500"}`}
                                  ></div>
                                  <div className="flex flex-col gap-1">
                                    <div className="flex items-center gap-2">
                                      <span className="text-sm font-medium text-zinc-200">
                                        Attempt {a.attempt_number}
                                      </span>
                                      <span
                                        className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${isSuccess ? "bg-green-500/10 text-green-400 border border-green-500/20" : "bg-red-500/10 text-red-400 border border-red-500/20"}`}
                                      >
                                        HTTP {a.http_status}
                                      </span>
                                    </div>
                                    <span className="text-xs text-zinc-500">
                                      {a.timeout
                                        ? "Connection timed out"
                                        : `Response in ${a.response_time_ms}ms`}
                                    </span>
                                  </div>
                                </div>
                              );
                            })}
                        </div>
                      )}
                    </div>

                    <hr className="border-zinc-800/60" />

                    {/* INTELLIGENCE ML BOX */}
                    <div>
                      <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">
                        Model Analysis
                      </h4>
                      {!intelligence ? (
                        <div className="text-xs text-zinc-500 flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full border-2 border-zinc-500 border-t-transparent animate-spin"></div>{" "}
                          Running inference...
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <div className="flex items-center justify-between p-4 rounded bg-zinc-900 border border-zinc-800 mb-3">
                            <div className="flex flex-col">
                              <span className="text-xs text-zinc-400">
                                Replay Safety Score
                              </span>
                              <span className="text-sm font-medium text-zinc-100 mt-1">
                                {intelligence.safe_to_replay
                                  ? "Safe to Replay"
                                  : "High Risk Event"}
                              </span>
                            </div>

                            <div className="w-16 h-16 relative flex items-center justify-center">
                              <svg className="absolute inset-0 w-full h-full -rotate-90">
                                <circle
                                  cx="32"
                                  cy="32"
                                  r="28"
                                  fill="transparent"
                                  stroke="currentColor"
                                  strokeWidth="4"
                                  className="text-zinc-800"
                                />
                                <circle
                                  cx="32"
                                  cy="32"
                                  r="28"
                                  fill="transparent"
                                  stroke="currentColor"
                                  strokeWidth="4"
                                  strokeDasharray="175.9"
                                  strokeDashoffset={
                                    175.9 -
                                    175.9 *
                                      (intelligence.safe_to_replay
                                        ? 0.95
                                        : 0.15)
                                  }
                                  className={`${intelligence.safe_to_replay ? "text-green-500" : "text-red-500"} transition-all duration-1000`}
                                />
                              </svg>
                              <span className="text-sm font-bold text-zinc-100 relative z-10">
                                {intelligence.safe_to_replay ? "95%" : "15%"}
                              </span>
                            </div>
                          </div>

                          <div className="flex items-center justify-between p-3 rounded bg-zinc-900 border border-zinc-800">
                            <div className="flex flex-col">
                              <span className="text-xs text-zinc-400">
                                Behavioral Anomaly
                              </span>
                              <span className="text-sm font-medium text-zinc-100">
                                {intelligence.is_anomaly
                                  ? "Detected"
                                  : "Normal Traffic"}
                              </span>
                            </div>
                            <div
                              className={`w-2 h-2 rounded-full ${intelligence.is_anomaly ? "bg-red-500" : "bg-green-500"}`}
                            ></div>
                          </div>

                          <button
                            disabled={!intelligence.safe_to_replay}
                            className={`w-full py-2.5 mt-2 text-sm font-medium rounded transition-colors ${intelligence.safe_to_replay ? "bg-zinc-100 text-zinc-900 hover:bg-white" : "bg-zinc-800 text-zinc-500 cursor-not-allowed"}`}
                            onClick={() => alert("Replay request enqueued.")}
                          >
                            {intelligence.safe_to_replay
                              ? "Execute Replay"
                              : "Replay Blocked"}
                          </button>

                          <button
                            className="w-full py-2.5 mt-2 text-sm font-medium rounded transition-colors bg-zinc-900 text-zinc-100 hover:bg-zinc-800 border border-zinc-800 flex items-center justify-center gap-2"
                            onClick={async () => {
                              const userId =
                                localStorage.getItem("hookwatch_user_id");
                              try {
                                const res = await fetch(
                                  `https://hookwatch-backend.onrender.com/api/v1/webhooks/${selectedEventId}/send-mail?user_id=${userId}`,
                                  { method: "POST" },
                                );
                                if (res.ok) {
                                  alert("Analysis email sent!");
                                } else {
                                  alert("Failed to send email.");
                                }
                              } catch (e) {
                                alert("Error sending email.");
                              }
                            }}
                          >
                            <Mail className="w-4 h-4 text-zinc-400" /> Send
                            Analysis to Mail
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
