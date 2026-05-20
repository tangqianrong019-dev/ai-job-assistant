"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";
import { AuthProvider, useAuth } from "@/lib/AuthProvider";
import { getAvatarUrl } from "@/lib/avatar";
import { apiPost } from "@/lib/api";
import "./globals.css";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        <AuthProvider>
          <LayoutShell>{children}</LayoutShell>
        </AuthProvider>
      </body>
    </html>
  );
}

function LayoutShell({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();

  // 未登录 — 全宽布局（Landing / Login 页面自己撑满）
  if (!loading && !user) {
    return <main className="min-h-screen">{children}</main>;
  }

  // 加载中
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
      </div>
    );
  }

  // 已登录 — Sidebar + Main
  return (
    <div className="flex">
      <Sidebar />
      <main className="ml-60 flex-1 px-8 py-8">{children}</main>
    </div>
  );
}

// ---------------------------------------------------------------------------
// MENU
// ---------------------------------------------------------------------------

const MENU = [
  { href: "/job-analysis", label: "JD 分析", icon: IconSearch },
  { href: "/resume-optimizer", label: "简历优化", icon: IconDoc },
  { href: "/mock-interview", label: "AI 模拟面试", icon: IconChat },
  { href: "/project-gen", label: "项目经历生成", icon: IconCode },
  { href: "/offer-compare", label: "Offer 对比", icon: IconCompare },
];

function Sidebar() {
  const pathname = usePathname();
  const { user, loading, signOut } = useAuth();
  const meta = (user?.user_metadata as { nickname?: string } | undefined);
  const nickname = meta?.nickname || user?.email?.split("@")[0] || "";

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-60 flex-col border-r border-indigo-100 bg-white shadow-sm">
      {/* Logo */}
      <div className="flex items-center gap-3 border-b border-indigo-100 px-5 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 text-sm font-bold text-white shadow shadow-indigo-200">
          AI
        </div>
        <span className="text-lg font-bold bg-gradient-to-r from-blue-700 to-indigo-700 bg-clip-text text-transparent">
          求职助手
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {MENU.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                active
                  ? "bg-gradient-to-r from-blue-50 to-indigo-50 text-indigo-700 shadow-sm"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              }`}
            >
              <Icon active={active} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* User */}
      <div className="border-t border-indigo-100 px-4 py-3">
        {loading ? (
          <p className="text-xs text-gray-400">加载中...</p>
        ) : user ? (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <img
                src={getAvatarUrl(nickname)}
                alt=""
                className="h-9 w-9 rounded-full ring-2 ring-indigo-100"
              />
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-medium text-gray-800">{nickname}</p>
                <p className="truncate text-[10px] text-gray-400">{user.email}</p>
              </div>
            </div>
            <UpgradeButton />
            <div className="flex gap-1">
              <Link href="/settings" className="flex-1 rounded border border-gray-200 px-2 py-1 text-center text-[10px] text-gray-500 hover:bg-gray-50">设置</Link>
              <button onClick={signOut} className="flex-1 rounded border border-gray-200 px-2 py-1 text-[10px] text-gray-500 hover:bg-gray-50">退出</button>
            </div>
          </div>
        ) : (
          <Link href="/login" className="block w-full rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-3 py-2.5 text-center text-xs font-bold text-white shadow shadow-indigo-200 transition hover:from-blue-700 hover:to-indigo-700">
            登录 / 注册
          </Link>
        )}
      </div>
    </aside>
  );
}

function UpgradeButton() {
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();
  if (!user) return null;
  async function handleUpgrade() {
    setLoading(true);
    try {
      const data = await apiPost<{ annual: boolean }>("/payment/create-checkout", { annual: false });
      window.location.href = data.checkout_url;
    } catch (e) {
      alert(`支付请求失败：${e instanceof Error ? e.message : "请求失败"}`);
      setLoading(false);
    }
  }
  return (
    <button onClick={handleUpgrade} disabled={loading} className="w-full rounded-lg bg-gradient-to-r from-amber-400 to-orange-500 px-2 py-1.5 text-xs font-bold text-white shadow shadow-orange-200 hover:from-amber-500 hover:to-orange-600 disabled:opacity-50">
      {loading ? "跳转中..." : "升级 Pro"}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Icons
// ---------------------------------------------------------------------------
const ac = (a: boolean) => a ? "#4f46e5" : "#9ca3af";
function IconSearch({ active }: { active: boolean }) {
  return <svg className="h-5 w-5" fill="none" stroke={ac(active)} strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"/></svg>;
}
function IconDoc({ active }: { active: boolean }) {
  return <svg className="h-5 w-5" fill="none" stroke={ac(active)} strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/></svg>;
}
function IconChat({ active }: { active: boolean }) {
  return <svg className="h-5 w-5" fill="none" stroke={ac(active)} strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155"/></svg>;
}
function IconCode({ active }: { active: boolean }) {
  return <svg className="h-5 w-5" fill="none" stroke={ac(active)} strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5"/></svg>;
}
function IconCompare({ active }: { active: boolean }) {
  return <svg className="h-5 w-5" fill="none" stroke={ac(active)} strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M3 7.5L7.5 3m0 0L12 7.5M7.5 3v13.5m13.5 0L16.5 21m0 0L12 16.5m4.5 4.5V7.5"/></svg>;
}
