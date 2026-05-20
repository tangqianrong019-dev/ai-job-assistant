"use client";

import { useState } from "react";
import { resumeOptimize, type ResumeOptimizeResult } from "@/lib/api";
import RequireAuth from "@/lib/RequireAuth";
import FileUploader, { type AttachedFile } from "@/lib/FileUploader";

export default function ResumeOptimizerPage() {
  return <RequireAuth><ResumeOptimizerContent /></RequireAuth>;
}

function ResumeOptimizerContent() {
  const [resumeText, setResumeText] = useState("");
  const [jdText, setJdText] = useState("");
  const [attachedFile, setAttachedFile] = useState<AttachedFile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ResumeOptimizeResult | null>(null);

  async function handleOptimize() {
    const resume = attachedFile?.text || resumeText;
    if (!resume.trim() || !jdText.trim()) {
      setError("请上传简历或填写简历内容，并填写目标岗位 JD");
      return;
    }
    setError("");
    setLoading(true);
    setResult(null);

    try {
      const data = await resumeOptimize(resume, jdText);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "请求失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold">简历优化</h1>
        <p className="mt-1 text-gray-500">
          AI 根据 JD 深度优化简历：挖掘隐藏优势、发现技能缺口、重写项目描述
        </p>
      </div>

      {/* Inputs */}
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <div className="mb-1 flex items-center justify-between">
            <label className="text-sm font-medium text-gray-700">简历内容</label>
            <FileUploader onFile={setAttachedFile} />
          </div>
          <textarea
            className="h-72 w-full rounded-lg border p-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="粘贴简历文本或上传文件..."
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">目标岗位 JD</label>
          <textarea
            className="h-72 w-full rounded-lg border p-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="粘贴目标职位描述..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
        </div>
      </div>

      {/* Button */}
      <div className="flex items-center gap-4">
        <button
          onClick={handleOptimize}
          disabled={loading}
          className="rounded-lg bg-blue-600 px-6 py-2.5 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "优化中..." : "开始优化"}
        </button>
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Summary banner */}
          <div className="rounded-xl border-l-4 border-blue-500 bg-blue-50 p-5">
            <p className="text-sm font-medium text-blue-800">{result.summary}</p>
          </div>

          {/* Strengths + Missing skills */}
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h3 className="mb-3 font-semibold text-green-700">
                优势挖掘 ({result.strength_discovery.length})
              </h3>
              <ul className="space-y-2">
                {result.strength_discovery.map((s, i) => (
                  <li key={i} className="flex gap-2 text-sm">
                    <span className="mt-0.5 shrink-0 text-green-500">+</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h3 className="mb-3 font-semibold text-red-700">
                缺失技能 ({result.missing_skills.length})
              </h3>
              <ul className="space-y-2">
                {result.missing_skills.map((s, i) => (
                  <li key={i} className="flex gap-2 text-sm">
                    <span className="mt-0.5 shrink-0 text-red-500">&ndash;</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Rewritten projects */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="mb-4 font-semibold text-blue-700">
              重写后的项目描述 ({result.rewritten_projects.length})
            </h3>
            <div className="space-y-5">
              {result.rewritten_projects.map((proj, i) => (
                <div key={i} className="grid gap-4 md:grid-cols-2">
                  <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                    <p className="mb-1 text-xs font-medium text-gray-400">原始版本</p>
                    <p className="text-sm text-gray-600">{proj.original}</p>
                  </div>
                  <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
                    <p className="mb-1 text-xs font-medium text-blue-400">优化版本</p>
                    <p className="text-sm text-blue-800">{proj.rewritten}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
