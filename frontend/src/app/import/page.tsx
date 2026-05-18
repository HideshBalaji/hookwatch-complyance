"use client";

import React, { useEffect, useState } from "react";
import {
  Activity,
  Server,
  UploadCloud,
  LogOut,
  FileJson,
  FileText,
  Database,
  Loader2,
  BarChart3,
} from "lucide-react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useToast } from "../ToastProvider";

export default function ImportData() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userName, setUserName] = useState("");
  const [activeTab, setActiveTab] = useState<
    "csv" | "json_bulk" | "json_single"
  >("csv");
  const [isUploading, setIsUploading] = useState(false);
  const { showToast } = useToast();

  const [jsonInput, setJsonInput] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("hookwatch_token");
    if (!token) {
      router.push("/login");
    } else {
      setIsAuthenticated(true);
      setUserName(localStorage.getItem("hookwatch_user_name") || "User");
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("hookwatch_token");
    localStorage.removeItem("hookwatch_user_id");
    localStorage.removeItem("hookwatch_user_name");
    router.push("/login");
  };

  const handleCSVUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    showToast({ message: "Starting upload task...", type: "loading" });

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
      const data = await res.json();

      if (res.ok && data.task_id) {
        const taskId = data.task_id;
        showToast({
          message: "Task registered. Beginning ingestion...",
          type: "loading",
          taskId: taskId,
        });
        const interval = setInterval(async () => {
          try {
            const statusRes = await fetch(
              `https://hookwatch-backend.onrender.com/api/v1/webhooks/upload/status/${taskId}`,
            );
            if (statusRes.ok) {
              const statusData = await statusRes.json();
              if (statusData.status === "processing") {
                showToast({
                  message: `Ingesting logs... ${statusData.processed} / ${statusData.total} events`,
                  type: "loading",
                  taskId: taskId,
                });
              } else if (statusData.status === "complete") {
                clearInterval(interval);
                setIsUploading(false);
                showToast({
                  message: `Successfully ingested ${statusData.processed} events and ${statusData.attempts_processed} attempts.`,
                  type: "success",
                });
              } else if (statusData.status === "failed") {
                clearInterval(interval);
                setIsUploading(false);
                showToast({
                  message: `Upload failed: ${statusData.error}`,
                  type: "error",
                });
              }
            }
          } catch (err) {
            // Ignore network blips during polling
          }
        }, 1000);
      } else {
        setIsUploading(false);
        showToast({ message: data.detail || "Upload failed", type: "error" });
      }
    } catch (e: any) {
      setIsUploading(false);
      showToast({
        message: e.message || "Network error occurred.",
        type: "error",
      });
    }
  };

  const handleJsonSubmit = async () => {
    setIsUploading(true);
    showToast({ message: "Ingesting JSON payload...", type: "loading" });
    const userId = localStorage.getItem("hookwatch_user_id");

    try {
      const parsedData = JSON.parse(jsonInput);
      const endpoint = activeTab === "json_bulk" ? "upload/bulk" : "upload";

      const res = await fetch(
        `https://hookwatch-backend.onrender.com/api/v1/webhooks/${endpoint}?user_id=${userId}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(parsedData),
        },
      );
      const data = await res.json();
      if (res.ok) {
        showToast({
          message: data.message || "Successfully ingested JSON data.",
          type: "success",
        });
        setJsonInput("");
      } else {
        showToast({ message: data.detail || "Upload failed", type: "error" });
      }
    } catch (e: any) {
      showToast({
        message: "Invalid JSON format or network error.",
        type: "error",
      });
    } finally {
      setIsUploading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex h-screen bg-zinc-950 items-center justify-center"></div>
    );
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
            <Link
              href="/"
              className="flex items-center gap-2.5 px-3 py-1.5 rounded hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 transition-colors"
            >
              <Activity className="w-4 h-4 text-zinc-500" />
              <span className="font-medium">Overview</span>
            </Link>
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
            <div className="flex items-center gap-2.5 px-3 py-1.5 rounded bg-zinc-800/80 text-zinc-100 mt-4">
              <UploadCloud className="w-4 h-4 text-zinc-400" />
              <span className="font-medium">Import Data</span>
            </div>
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
            Data Ingestion
          </h2>
        </header>

        <div className="p-6 max-w-[1000px]">
          <div className="ui-panel p-6">
            <p className="text-zinc-400 mb-6">
              Select an ingestion method to manually upload webhook delivery
              logs into your workspace database.
            </p>

            <div className="flex border-b border-zinc-800 mb-6">
              <button
                onClick={() => setActiveTab("csv")}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === "csv" ? "border-zinc-100 text-zinc-100" : "border-transparent text-zinc-500 hover:text-zinc-300"}`}
              >
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4" /> Batch CSV Upload
                </div>
              </button>
              <button
                onClick={() => setActiveTab("json_bulk")}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === "json_bulk" ? "border-zinc-100 text-zinc-100" : "border-transparent text-zinc-500 hover:text-zinc-300"}`}
              >
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4" /> Bulk JSON Array
                </div>
              </button>
              <button
                onClick={() => setActiveTab("json_single")}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === "json_single" ? "border-zinc-100 text-zinc-100" : "border-transparent text-zinc-500 hover:text-zinc-300"}`}
              >
                <div className="flex items-center gap-2">
                  <FileJson className="w-4 h-4" /> Single JSON Event
                </div>
              </button>
            </div>

            {activeTab === "csv" && (
              <div
                className={`flex flex-col items-center justify-center p-12 border rounded transition-colors ${isUploading ? "border-zinc-600 bg-zinc-900" : "border-dashed border-zinc-700 bg-zinc-900/50"}`}
              >
                {isUploading ? (
                  <Loader2 className="w-10 h-10 text-zinc-400 mb-4 animate-spin" />
                ) : (
                  <FileText className="w-10 h-10 text-zinc-600 mb-4" />
                )}

                <h3 className="text-zinc-200 font-medium mb-1">
                  {isUploading ? "Uploading..." : "Upload CSV Logs"}
                </h3>
                <p className="text-zinc-500 text-xs mb-6 max-w-sm text-center">
                  {isUploading
                    ? "Please wait while we parse and ingest the data into the database. You can navigate away from this page safely."
                    : "Upload a CSV file containing columns for event_id, event_type, created_at, endpoint_id, attempt_number, http_status, response_time_ms, and timeout."}
                </p>

                {!isUploading && (
                  <label className="px-4 py-2 rounded bg-zinc-100 text-zinc-900 font-medium hover:bg-white transition-colors cursor-pointer disabled:opacity-50">
                    Browse Files
                    <input
                      type="file"
                      accept=".csv"
                      className="hidden"
                      onChange={handleCSVUpload}
                      disabled={isUploading}
                    />
                  </label>
                )}
              </div>
            )}

            {(activeTab === "json_bulk" || activeTab === "json_single") && (
              <div className="flex flex-col gap-4">
                <div>
                  <label className="block text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                    {activeTab === "json_bulk"
                      ? "Paste JSON Array"
                      : "Paste JSON Object"}
                  </label>
                  <textarea
                    className="w-full h-64 bg-zinc-950 border border-zinc-800 rounded p-4 text-xs font-mono text-zinc-300 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-600"
                    placeholder={
                      activeTab === "json_bulk"
                        ? '[\n  {\n    "event_id": "...",\n    "event_type": "...",\n    ...\n  }\n]'
                        : '{\n  "event_id": "...",\n  "event_type": "...",\n  ...\n}'
                    }
                    value={jsonInput}
                    onChange={(e) => setJsonInput(e.target.value)}
                  />
                </div>
                <button
                  onClick={handleJsonSubmit}
                  disabled={isUploading || !jsonInput.trim()}
                  className="self-start px-4 py-2 rounded bg-zinc-100 text-zinc-900 font-medium hover:bg-white transition-colors disabled:opacity-50"
                >
                  {isUploading ? "Processing..." : "Submit JSON"}
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
