"use client";

import { useState } from "react";
import { jdMatch, type JDMatchResult } from "@/lib/api";
import RequireAuth from "@/lib/RequireAuth";
import FileUploader, { type AttachedFile } from "@/lib/FileUploader";

export default function JobAnalysisPage() {
  return <RequireAuth><JobAnalysisContent /></RequireAuth>;
}

function JobAnalysisContent() {
  const [resumeText, setResumeText] = useState("");
  const [jdText, setJdText] = useState("");
  const [attachedFile, setAttachedFile] = useState<AttachedFile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<JDMatchResult | null>(null);

  async function handleAnalyze() {
    const resume = attachedFile?.text || resumeText;
    if (!resume.trim() || !jdText.trim()) {
      setError("请上传简历或填写简历内容，并填写 JD 内容");
      return;
    }
    setError("");
    setLoading(true);
    setResult(null);

    try {
      const data = await jdMatch(resume, jdText);
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
        <h1 className="text-2xl font-bold">JD 匹配分析</h1>
        <p className="mt-1 text-gray-500">
          粘贴简历内容和职位描述，AI 将分析匹配度并给出改进建议
        </p>
      </div>

      {/* Text inputs */}
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
          <label className="mb-1 block text-sm font-medium text-gray-700">
            JD 内容
          </label>
          <textarea
            className="h-72 w-full rounded-lg border p-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="粘贴职位描述..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
        </div>
      </div>

      {/* Button */}
      <div className="flex items-center gap-4">
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="rounded-lg bg-blue-600 px-6 py-2.5 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "分析中..." : "开始分析"}
        </button>
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Match score */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-700 text-2xl font-bold text-white">
                {result.match_percentage}%
              </div>
              <div>
                <h3 className="text-lg font-semibold">匹配度</h3>
                <p className="text-sm text-gray-500">{result.match_summary}</p>
              </div>
            </div>
          </div>

          {/* Core overlap + Missing skills */}
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h3 className="mb-3 font-semibold text-green-700">
                核心技能重合 ({result.core_overlap.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {result.core_overlap.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-full bg-green-50 px-3 py-1 text-sm text-green-700"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div className="rounded-xl border bg-white p-6 shadow-sm">
              <h3 className="mb-3 font-semibold text-red-700">
                缺失技能 ({result.missing_skills.length})
              </h3>
              <ul className="space-y-2">
                {result.missing_skills.map((s) => (
                  <li key={s.skill} className="flex items-center gap-2 text-sm">
                    <span className="text-red-500">&ndash;</span>
                    <span>{s.skill}</span>
                    <span
                      className={`rounded px-1.5 py-0.5 text-xs ${
                        s.importance === "required"
                          ? "bg-red-100 text-red-700"
                          : s.importance === "preferred"
                            ? "bg-yellow-100 text-yellow-700"
                            : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {s.importance === "required"
                        ? "必须"
                        : s.importance === "preferred"
                          ? "加分"
                          : "优先"}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Suggestions */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="mb-3 font-semibold text-blue-700">
              改进建议 ({result.suggestions.length})
            </h3>
            <ol className="space-y-3">
              {result.suggestions.map((s, i) => (
                <li key={i} className="flex gap-3 text-sm">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                    {i + 1}
                  </span>
                  <span className="pt-0.5">{s}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </div>
  );
}
