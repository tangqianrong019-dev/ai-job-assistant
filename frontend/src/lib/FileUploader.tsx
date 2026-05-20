"use client";

import { useState } from "react";
import { getToken } from "./supabaseClient";

export interface AttachedFile {
  name: string;
  text: string;   // 解析后的文本，传给 AI 分析
  size: string;
}

export default function FileUploader({ onFile }: { onFile: (f: AttachedFile | null) => void }) {
  const [attached, setAttached] = useState<AttachedFile | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    setSuccess(false);

    try {
      const token = await getToken();
      if (!token) throw new Error("请先登录");

      const form = new FormData();
      form.append("file", file);

      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const res = await fetch(`${API_BASE}/files/parse`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      if (!res.ok) throw new Error(`解析失败 (${res.status})`);

      const data = await res.json();
      const f: AttachedFile = {
        name: file.name,
        text: data.text,
        size: formatSize(file.size),
      };
      setAttached(f);
      onFile(f);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "上传失败");
    } finally {
      setUploading(false);
    }
  }

  function handleRemove() {
    setAttached(null);
    onFile(null);
    setSuccess(false);
  }

  return (
    <div>
      {/* Upload / Replace button */}
      <label className="inline-flex cursor-pointer items-center gap-1 text-xs text-indigo-600 hover:text-indigo-700">
        <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        <input type="file" accept=".pdf,.docx,.doc,.txt" onChange={handleUpload} className="hidden" />
        {uploading ? "上传中..." : attached ? "更换文件" : "上传 PDF/Word"}
      </label>
      {success && <span className="ml-2 text-xs text-green-600">上传成功</span>}
      {error && <span className="ml-2 text-xs text-red-500">{error}</span>}

      {/* Attachment card */}
      {attached && (
        <div className="mt-2 flex items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 px-4 py-2.5">
          <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${attached.name.endsWith(".pdf") ? "bg-red-100" : "bg-blue-100"}`}>
            <span className={`text-sm font-bold ${attached.name.endsWith(".pdf") ? "text-red-500" : "text-blue-600"}`}>
              {attached.name.endsWith(".pdf") ? "PDF" : "DOC"}
            </span>
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-gray-700">{attached.name}</p>
            <p className="text-xs text-gray-400">{attached.size}</p>
          </div>
          <button onClick={handleRemove} className="shrink-0 text-lg leading-none text-gray-300 hover:text-red-500" title="移除">
            ×
          </button>
        </div>
      )}
    </div>
  );
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(1)} MB`;
}
