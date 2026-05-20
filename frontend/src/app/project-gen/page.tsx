"use client";

import { useState } from "react";
import { projectGen } from "@/lib/api";
import RequireAuth from "@/lib/RequireAuth";

export default function ProjectGenPage() {
  return <RequireAuth><ProjectGenContent /></RequireAuth>;
}

function ProjectGenContent() {
  const [projectName, setProjectName] = useState("");
  const [techStack, setTechStack] = useState("");
  const [achievements, setAchievements] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [markdown, setMarkdown] = useState("");

  async function handleGenerate() {
    if (!projectName.trim() || !techStack.trim() || !achievements.trim()) {
      setError("请填写所有字段");
      return;
    }
    setError("");
    setLoading(true);
    setMarkdown("");

    try {
      const data = await projectGen(projectName, techStack, achievements);
      setMarkdown(data.markdown);
    } catch (e) {
      setError(e instanceof Error ? e.message : "请求失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold">项目经历生成</h1>
        <p className="mt-1 text-gray-500">
          输入项目关键词，AI 自动扩写为符合 STAR 原则的简历项目描述
        </p>
      </div>

      {/* Input form */}
      <div className="space-y-4 rounded-xl border bg-white p-6 shadow-sm">
        <div>
          <label className="mb-1 block text-sm font-medium">项目名称</label>
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="例如：电商订单系统重构"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">核心技术栈</label>
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="例如：Spring Cloud, Redis, Kafka, MySQL"
            value={techStack}
            onChange={(e) => setTechStack(e.target.value)}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">主要成就</label>
          <textarea
            className="h-24 w-full rounded-lg border p-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="例如：QPS提升300%, 订单延迟降低50%, 支撑日均10万+订单"
            value={achievements}
            onChange={(e) => setAchievements(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="rounded-lg bg-blue-600 px-6 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "生成中..." : "生成描述"}
          </button>
          {error && <p className="text-sm text-red-500">{error}</p>}
        </div>
      </div>

      {/* Result */}
      {markdown && (
        <div className="rounded-xl border bg-white shadow-sm">
          <div className="flex items-center justify-between border-b px-5 py-3">
            <h3 className="font-semibold text-gray-800">生成结果</h3>
            <button
              onClick={() => navigator.clipboard.writeText(markdown)}
              className="rounded border px-3 py-1 text-xs text-gray-500 hover:bg-gray-100"
            >
              复制
            </button>
          </div>
          <div className="prose prose-sm max-w-none p-6 whitespace-pre-wrap font-mono text-sm leading-relaxed text-gray-700">
            {markdown}
          </div>
        </div>
      )}
    </div>
  );
}
