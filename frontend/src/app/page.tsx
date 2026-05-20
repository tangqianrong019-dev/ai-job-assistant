"use client";

import Link from "next/link";
import { useAuth } from "@/lib/AuthProvider";

const FEATURES = [
  { title: "JD 匹配分析", desc: "AI 深度对比简历与岗位描述，精准评估匹配度，量化技能差距", icon: "🔍" },
  { title: "简历智能优化", desc: "挖掘隐藏优势，STAR 法则重写项目经历，让简历脱颖而出", icon: "📄" },
  { title: "AI 模拟面试", desc: "根据目标岗位定制面试题，实时评分反馈，提前演练", icon: "💬" },
  { title: "项目经历生成", desc: "输入关键词，AI 自动扩写为专业的 STAR 原则项目描述", icon: "⚡" },
  { title: "Offer 对比", desc: "多维度评分，综合分析建议，辅助你的职业决策", icon: "📊" },
];

export default function HomePage() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  // 已登录 → 不展示 Landing（由 sidebar + children 展示）
  if (user) {
    return (
      <div className="space-y-8 py-8 text-center">
        <h1 className="text-3xl font-bold">欢迎回来 👋</h1>
        <p className="text-gray-500">从左侧菜单选择功能开始</p>
      </div>
    );
  }

  // 未登录 → Landing 页
  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700 px-8 pb-20 pt-24 text-center text-white">
        <div className="mx-auto max-w-2xl">
          <span className="inline-block rounded-full border border-white/30 bg-white/10 px-4 py-1 text-sm backdrop-blur">
            AI 驱动的智能求职助手
          </span>
          <h1 className="mt-6 text-4xl font-extrabold tracking-tight sm:text-5xl">
            让 AI 帮你拿下
            <span className="block text-indigo-200">心仪的 Offer</span>
          </h1>
          <p className="mt-5 text-lg text-blue-100">
            简历优化、模拟面试、岗位匹配 — 一站式 AI 求职平台
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link
              href="/login"
              className="rounded-xl bg-white px-8 py-3.5 font-bold text-blue-700 shadow-lg shadow-blue-900/30 transition hover:bg-blue-50"
            >
              免费开始使用
            </Link>
            <span className="text-sm text-blue-200">免费 5 次 · 无需绑定信用卡</span>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-white px-8 py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-10 text-center text-2xl font-bold text-gray-900">
            五大核心功能
          </h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f) => (
              <div
                key={f.title}
                className="group rounded-2xl border border-gray-100 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
              >
                <div className="mb-3 text-3xl">{f.icon}</div>
                <h3 className="mb-2 text-lg font-semibold text-gray-900">{f.title}</h3>
                <p className="text-sm leading-relaxed text-gray-500">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="border-t bg-gray-50 px-8 py-20 text-center">
        <h2 className="text-2xl font-bold text-gray-900">准备好开始了吗？</h2>
        <p className="mt-2 text-gray-500">注册即可免费使用 5 次，体验 AI 驱动的求职效率</p>
        <Link
          href="/login"
          className="mt-6 inline-block rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-3 font-bold text-white shadow-lg shadow-blue-200 transition hover:from-blue-700 hover:to-indigo-700"
        >
          立即注册
        </Link>
      </section>
    </div>
  );
}
