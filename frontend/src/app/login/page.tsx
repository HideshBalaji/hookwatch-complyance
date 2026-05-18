"use client";

import React, { useState } from "react";
import { Activity } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("https://hookwatch-backend.onrender.com/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Login failed");
      }

      localStorage.setItem("hookwatch_token", data.access_token);
      localStorage.setItem("hookwatch_user_id", data.user_id);
      localStorage.setItem("hookwatch_user_name", data.name);

      router.push("/");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-zinc-950 items-center justify-center p-4 font-sans selection:bg-zinc-800 selection:text-zinc-100">
      <div className="w-full max-w-[360px] flex flex-col gap-6">
        <div className="flex flex-col items-center mb-2">
          <div className="w-10 h-10 flex items-center justify-center mb-4">
            <Activity className="w-6 h-6 text-zinc-100" />
          </div>
          <h1 className="text-xl font-medium tracking-tight text-zinc-100">
            Sign in to HookWatch
          </h1>
        </div>

        <div className="ui-panel p-6">
          <form className="space-y-4" onSubmit={handleLogin}>
            {error && (
              <div className="p-3 rounded bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-medium">
                {error}
              </div>
            )}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-300">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded focus:outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 text-sm text-zinc-100 placeholder:text-zinc-600 transition-colors"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-medium text-zinc-300">
                  Password
                </label>
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-3 py-2 bg-zinc-900 border border-zinc-800 rounded focus:outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 text-sm text-zinc-100 placeholder:text-zinc-600 transition-colors"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2 rounded bg-zinc-100 hover:bg-white text-zinc-900 text-sm font-medium transition-colors disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>
        </div>

        <p className="text-center text-sm text-zinc-500">
          Don't have an account?{" "}
          <Link
            href="/signup"
            className="text-zinc-300 hover:text-white font-medium transition-colors"
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
