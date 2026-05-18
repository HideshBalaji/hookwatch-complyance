"use client";

import React, { useEffect, useState } from 'react';
import { Activity, Server, UploadCloud, LogOut, BarChart3, TrendingUp, AlertTriangle, ShieldCheck, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useToast } from '../ToastProvider';

interface InstabilityData {
  endpoint_id: string;
  total_attempts: number;
  failure_count: number;
  timeout_count: number;
  avg_response_time: number;
  failure_rate: number;
  timeout_rate: number;
}

interface RetryPatternData {
  attempt_number: number;
  count: number;
  avg_response_time: number;
  success_rate_percent: number;
}

interface ReplayData {
  replay_result: string;
  count: number;
  duplicates_detected: number;
}

export default function AnalyticsPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userName, setUserName] = useState('');
  const { showToast } = useToast();

  const [instability, setInstability] = useState<InstabilityData[]>([]);
  const [retryPatterns, setRetryPatterns] = useState<RetryPatternData[]>([]);
  const [replays, setReplays] = useState<ReplayData[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('hookwatch_token');
    if (!token) {
      router.push('/login');
    } else {
      setIsAuthenticated(true);
      setUserName(localStorage.getItem('hookwatch_user_name') || 'User');
      fetchAnalytics();
    }
  }, [router]);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const [instRes, retryRes, replayRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/v1/analytics/endpoints/instability'),
        fetch('http://127.0.0.1:8000/api/v1/analytics/retry/patterns'),
        fetch('http://127.0.0.1:8000/api/v1/analytics/replays')
      ]);

      if (instRes.ok && retryRes.ok && replayRes.ok) {
        const instData = await instRes.json();
        const retryData = await retryRes.json();
        const replayData = await replayRes.json();

        setInstability(instData.endpoints || []);
        setRetryPatterns(retryData.patterns || []);
        setReplays(replayData.replays || []);
      } else {
        showToast({ message: "Failed to load some analytics data.", type: "error" });
      }
    } catch (error) {
      showToast({ message: "Network error loading analytics.", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('hookwatch_token');
    localStorage.removeItem('hookwatch_user_id');
    localStorage.removeItem('hookwatch_user_name');
    router.push('/login');
  };

  if (!isAuthenticated) {
    return <div className="flex h-screen bg-zinc-950 items-center justify-center"></div>;
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
            <Link href="/" className="flex items-center gap-2.5 px-3 py-1.5 rounded hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 transition-colors">
              <Activity className="w-4 h-4 text-zinc-500" />
              <span className="font-medium">Overview</span>
            </Link>
            <Link href="/endpoints" className="flex items-center gap-2.5 px-3 py-1.5 rounded hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 transition-colors">
              <Server className="w-4 h-4 text-zinc-500" />
              <span className="font-medium">Endpoints</span>
            </Link>
            <div className="flex items-center gap-2.5 px-3 py-1.5 rounded bg-zinc-800/80 text-zinc-100">
              <BarChart3 className="w-4 h-4 text-zinc-400" />
              <span className="font-medium">Analytics</span>
            </div>
            <Link href="/import" className="flex items-center gap-2.5 px-3 py-1.5 rounded hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200 transition-colors mt-4">
              <UploadCloud className="w-4 h-4 text-zinc-500" />
              <span className="font-medium">Import Data</span>
            </Link>
          </nav>
        </div>

        <div className="p-3">
          <div className="px-3 py-2 text-xs font-medium text-zinc-500 truncate mb-1">{userName}</div>
          <button onClick={handleLogout} className="flex items-center gap-2.5 w-full px-3 py-1.5 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 transition-colors text-left">
            <LogOut className="w-4 h-4 text-zinc-500" />
            <span className="font-medium">Sign out</span>
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col h-full bg-zinc-950 overflow-y-auto">
        <header className="px-6 py-4 flex items-center justify-between border-b border-zinc-800/60 sticky top-0 bg-zinc-950 z-10">
          <h2 className="text-lg font-medium text-zinc-100 tracking-tight">Advanced Analytics</h2>
          <button onClick={fetchAnalytics} className="text-xs text-zinc-400 hover:text-zinc-200 transition-colors">
            Refresh Data
          </button>
        </header>

        <div className="p-6 space-y-6 max-w-[1200px]">
          
          {/* TOP SECTION: TWO CARDS */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* ENDPOINT INSTABILITY */}
            <div className="ui-panel p-6 flex flex-col h-[400px]">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                <h3 className="text-sm font-semibold text-zinc-100 uppercase tracking-wider">Endpoint Instability (Top Failing)</h3>
              </div>
              <p className="text-xs text-zinc-500 mb-4">Endpoints ranked by failure rate (requires &gt;5 attempts to rank).</p>
              
              <div className="flex-1 overflow-y-auto">
                {isLoading ? (
                  <div className="flex items-center justify-center h-full text-zinc-500 text-xs gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-zinc-600" />
                    Loading instability data...
                  </div>
                ) : instability.length === 0 ? (
                  <div className="text-zinc-600 text-xs p-4">No unstable endpoints detected with sufficient data.</div>
                ) : (
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="text-zinc-500 border-b border-zinc-800/60">
                        <th className="py-2 font-medium">Endpoint ID</th>
                        <th className="py-2 font-medium">Fail Rate</th>
                        <th className="py-2 font-medium">Timeouts</th>
                        <th className="py-2 font-medium">Avg Latency</th>
                      </tr>
                    </thead>
                    <tbody>
                      {instability.map((item, idx) => (
                        <tr key={idx} className="border-b border-zinc-800/40 hover:bg-zinc-900/50">
                          <td className="py-2.5 font-mono text-zinc-300">{item.endpoint_id}</td>
                          <td className="py-2.5 text-zinc-200">
                            <span className={`px-1.5 py-0.5 rounded-sm ${item.failure_rate > 0.5 ? 'bg-red-500/10 text-red-400' : 'bg-amber-500/10 text-amber-400'}`}>
                              {(item.failure_rate * 100).toFixed(1)}%
                            </span>
                          </td>
                          <td className="py-2.5 text-zinc-400">{item.timeout_count}</td>
                          <td className="py-2.5 text-zinc-400">{item.avg_response_time.toFixed(0)}ms</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>

            {/* RETRY PATTERNS */}
            <div className="ui-panel p-6 flex flex-col h-[400px]">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-4 h-4 text-emerald-500" />
                <h3 className="text-sm font-semibold text-zinc-100 uppercase tracking-wider">Retry Effectiveness</h3>
              </div>
              <p className="text-xs text-zinc-500 mb-4">Success rate analyzed by attempt number.</p>
              
              <div className="flex-1 overflow-y-auto flex flex-col justify-center gap-4">
                {isLoading ? (
                  <div className="flex items-center justify-center h-full text-zinc-500 text-xs gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-zinc-600" />
                    Loading retry patterns...
                  </div>
                ) : retryPatterns.length === 0 ? (
                  <div className="text-zinc-600 text-xs p-4">No retry data available.</div>
                ) : (
                  retryPatterns.map((pattern, idx) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-zinc-300 font-medium">Attempt #{pattern.attempt_number}</span>
                        <span className="text-zinc-400">{pattern.success_rate_percent.toFixed(1)}% Success</span>
                      </div>
                      <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all duration-500 ${pattern.success_rate_percent > 70 ? 'bg-emerald-600' : pattern.success_rate_percent > 30 ? 'bg-amber-600' : 'bg-red-600'}`}
                          style={{ width: `${pattern.success_rate_percent}%` }}
                        ></div>
                      </div>
                      <div className="text-[10px] text-zinc-600">
                        Volume: {pattern.count} reqs | Avg Latency: {pattern.avg_response_time.toFixed(0)}ms
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

          </div>

          {/* BOTTOM SECTION: REPLAY FREQUENCY */}
          <div className="ui-panel p-6">
            <div className="flex items-center gap-2 mb-4">
              <ShieldCheck className="w-4 h-4 text-blue-500" />
              <h3 className="text-sm font-semibold text-zinc-100 uppercase tracking-wider">Replay Execution Intelligence</h3>
            </div>
            <p className="text-xs text-zinc-500 mb-6">Metrics tracking the outcome of manual and automatic replay actions.</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {isLoading ? (
                <div className="flex items-center justify-center h-full text-zinc-500 text-xs gap-2 col-span-3">
                  <Loader2 className="w-4 h-4 animate-spin text-zinc-600" />
                  Loading replay metrics...
                </div>
              ) : replays.length === 0 ? (
                <div className="text-zinc-600 text-xs p-4 col-span-3">No replay execution data found.</div>
              ) : (
                replays.map((replay, idx) => (
                  <div key={idx} className="bg-zinc-900/50 border border-zinc-800/60 rounded-lg p-5 flex flex-col justify-between">
                    <div>
                      <div className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-1">{replay.replay_result || 'Unknown'}</div>
                      <div className="text-2xl font-bold text-zinc-100 tabular-nums">{replay.count}</div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-zinc-800/60 flex justify-between text-xs">
                      <span className="text-zinc-500">Duplicates Avoided</span>
                      <span className="text-zinc-300 font-mono font-medium">{replay.duplicates_detected}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
