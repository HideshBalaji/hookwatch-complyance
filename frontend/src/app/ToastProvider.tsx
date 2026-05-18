"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";

type ToastType = "loading" | "success" | "error";

interface ToastOptions {
  message: string;
  type: ToastType;
  taskId?: string;
}

interface ToastContextType {
  showToast: (options: ToastOptions) => void;
  hideToast: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toast, setToast] = useState<ToastOptions | null>(null);

  useEffect(() => {
    // Restore toast on refresh
    const savedToast = sessionStorage.getItem("hookwatch_toast");
    if (savedToast) {
      const parsed = JSON.parse(savedToast) as ToastOptions;
      if (parsed.type !== "loading") {
        setToast(parsed);
        setTimeout(() => {
          setToast(null);
          sessionStorage.removeItem("hookwatch_toast");
        }, 5000);
      } else {
        if (parsed.taskId) {
          setToast(parsed);
          // Resume background polling after full page refresh
          const interval = setInterval(async () => {
            try {
              const statusRes = await fetch(
                `https://hookwatch-backend.onrender.com/api/v1/webhooks/upload/status/${parsed.taskId}`,
              );
              if (statusRes.ok) {
                const statusData = await statusRes.json();
                if (statusData.status === "processing") {
                  setToast({
                    message: `Ingesting logs... ${statusData.processed} / ${statusData.total} events`,
                    type: "loading",
                    taskId: parsed.taskId,
                  });
                  sessionStorage.setItem(
                    "hookwatch_toast",
                    JSON.stringify({
                      message: `Ingesting logs... ${statusData.processed} / ${statusData.total} events`,
                      type: "loading",
                      taskId: parsed.taskId,
                    }),
                  );
                } else if (statusData.status === "complete") {
                  clearInterval(interval);
                  const successToast: ToastOptions = {
                    message: `Successfully ingested ${statusData.processed} events and ${statusData.attempts_processed} attempts.`,
                    type: "success",
                  };
                  setToast(successToast);
                  sessionStorage.setItem(
                    "hookwatch_toast",
                    JSON.stringify(successToast),
                  );
                  setTimeout(() => {
                    setToast(null);
                    sessionStorage.removeItem("hookwatch_toast");
                  }, 5000);
                } else if (statusData.status === "failed") {
                  clearInterval(interval);
                  const errToast: ToastOptions = {
                    message: `Upload failed: ${statusData.error}`,
                    type: "error",
                  };
                  setToast(errToast);
                  sessionStorage.setItem(
                    "hookwatch_toast",
                    JSON.stringify(errToast),
                  );
                  setTimeout(() => {
                    setToast(null);
                    sessionStorage.removeItem("hookwatch_toast");
                  }, 5000);
                }
              }
            } catch (err) {}
          }, 1000);
        } else {
          sessionStorage.removeItem("hookwatch_toast");
        }
      }
    }
  }, []);

  const showToast = (options: ToastOptions) => {
    setToast(options);
    sessionStorage.setItem("hookwatch_toast", JSON.stringify(options));

    if (options.type !== "loading") {
      setTimeout(() => {
        setToast((current) => {
          if (current?.message === options.message) {
            sessionStorage.removeItem("hookwatch_toast");
            return null;
          }
          return current;
        });
      }, 5000);
    }
  };

  const hideToast = () => {
    setToast(null);
    sessionStorage.removeItem("hookwatch_toast");
  };

  return (
    <ToastContext.Provider value={{ showToast, hideToast }}>
      {children}
      {toast && (
        <div
          className={`fixed top-6 right-6 z-[100] flex items-center gap-3 px-4 py-3 bg-zinc-900 border rounded-lg shadow-xl text-zinc-100 text-sm font-medium transition-all animate-in slide-in-from-top-5 ${toast.type === "success" ? "border-green-500 shadow-[0_0_15px_rgba(34,197,94,0.15)]" : toast.type === "error" ? "border-red-500" : "border-zinc-700"}`}
        >
          {toast.type === "loading" && (
            <Loader2 className="w-5 h-5 text-zinc-400 animate-spin" />
          )}
          {toast.type === "success" && (
            <CheckCircle2 className="w-5 h-5 text-green-500" />
          )}
          {toast.type === "error" && (
            <XCircle className="w-5 h-5 text-red-500" />
          )}
          <span>{toast.message}</span>
        </div>
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}
