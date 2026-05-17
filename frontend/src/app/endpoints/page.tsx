"use client";

import React, { useEffect, useState } from 'react';
import { Activity, Server, UploadCloud, LogOut } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Endpoints() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [endpoints, setEndpoints] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('hookwatch_token');
    if (!token) {
      router.push('/login');
    } else {
      setIsAuthenticated(true);
      setUserName(localStorage.getItem('hookwatch_user_name') || 'User');
      const userId = localStorage.getItem('hookwatch_user_id');
      if (userId) {
        fetchEndpoints(userId);
      }
    }
  }, [router]);

  const fetchEndpoints = async (userId: string) => {
    try {
      const res = await fetch(`https://hookwatch-backend.onrender.com/api/v1/auth/endpoints?user_id=${userId}`);
      if (res.ok) {
        setEndpoints(await res.json());
      }
    } catch (err) {
      console.error("Failed to fetch endpoints:", err);
    } finally {
      setLoading(false);
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
            <div className="flex items-center gap-2.5 px-3 py-1.5 rounded bg-zinc-800/80 text-zinc-100">
              <Server className="w-4 h-4 text-zinc-400" />
              <span className="font-medium">Endpoints</span>
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
          <h2 className="text-lg font-medium text-zinc-100 tracking-tight">Registered Endpoints</h2>
        </header>

        <div className="p-6 max-w-[1600px]">
          <div className="grid grid-cols-3 gap-4">
            {loading ? (
                <div className="col-span-3 text-zinc-500 text-sm">Loading endpoints...</div>
            ) : endpoints.length === 0 ? (
                <div className="col-span-3 ui-panel p-8 text-center text-zinc-500">
                    <Server className="w-6 h-6 mx-auto mb-2 text-zinc-700" />
                    No endpoints registered.
                </div>
            ) : (
                endpoints.map((ep) => (
                    <div key={ep.endpoint_id} className="ui-panel p-5 flex flex-col gap-4">
                        <div className="flex justify-between items-start">
                            <div>
                                <div className="text-[10px] text-zinc-500 uppercase tracking-widest font-semibold mb-0.5">Destination</div>
                                <div className="text-base font-medium text-zinc-200 font-mono">{ep.endpoint_id}</div>
                            </div>
                            <div className="w-8 h-8 rounded border border-zinc-800 flex items-center justify-center">
                                <Server className="w-4 h-4 text-zinc-500" />
                            </div>
                        </div>

                        <div className="flex items-baseline gap-2 mt-2">
                            <span className={`text-2xl font-semibold ${ep.health_score > 90 ? 'text-green-500' : ep.health_score > 70 ? 'text-amber-500' : 'text-red-500'}`}>
                                {ep.health_score}%
                            </span>
                            <span className="text-zinc-500 text-xs font-medium uppercase tracking-wider">Health Score</span>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mt-2 pt-4 border-t border-zinc-800/60">
                            <div>
                                <div className="text-[10px] text-zinc-500 uppercase tracking-widest mb-1 font-semibold">Total Req</div>
                                <div className="text-zinc-200 font-medium">{ep.total_requests.toLocaleString()}</div>
                            </div>
                            <div>
                                <div className="text-[10px] text-zinc-500 uppercase tracking-widest mb-1 font-semibold">Failures</div>
                                <div className={`font-medium ${ep.failed_requests > 0 ? 'text-red-400' : 'text-zinc-200'}`}>
                                    {ep.failed_requests.toLocaleString()}
                                </div>
                            </div>
                        </div>
                    </div>
                ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
