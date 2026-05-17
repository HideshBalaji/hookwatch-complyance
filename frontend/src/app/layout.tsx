import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ToastProvider } from "./ToastProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "HookWatch Command Center",
  description: "Enterprise Webhook Intelligence & Replay Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-zinc-950 text-zinc-300 antialiased min-h-screen selection:bg-zinc-800 selection:text-zinc-100`}>
        <ToastProvider>
          {children}
        </ToastProvider>
      </body>
    </html>
  );
}
