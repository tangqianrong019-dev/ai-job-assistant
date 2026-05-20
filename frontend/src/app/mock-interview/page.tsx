"use client";

import { useState, useRef, useEffect } from "react";
import { interviewStart, interviewAnswer, type InterviewStartResult, type InterviewAnswerResult } from "@/lib/api";
import RequireAuth from "@/lib/RequireAuth";
import FileUploader, { type AttachedFile } from "@/lib/FileUploader";

interface Message {
  role: "interviewer" | "user" | "score";
  content: string;
  score?: number;
  suggestions?: string[];
}

export default function MockInterviewPage() {
  return <RequireAuth><MockInterviewContent /></RequireAuth>;
}

function MockInterviewContent() {
  const [jdText, setJdText] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [attachedFile, setAttachedFile] = useState<AttachedFile | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [total, setTotal] = useState(5);
  const [started, setStarted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [complete, setComplete] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleStart() {
    if (!jdText.trim()) return;
    setLoading(true);
    try {
      const data: InterviewStartResult = await interviewStart(jdText, attachedFile?.text || resumeText, total);
      setSessionId(data.session_id);
      setStarted(true);
      setMessages([
        {
          role: "interviewer",
          content: `面试开始！共 ${data.total} 题。\n\n${data.question}`,
        },
      ]);
    } catch {
      setMessages([{ role: "interviewer", content: "启动面试失败，请检查后端是否运行。" }]);
      setStarted(true);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmitAnswer() {
    if (!answer.trim() || !sessionId) return;
    const userAnswer = answer;
    setAnswer("");
    setMessages((prev) => [...prev, { role: "user", content: userAnswer }]);
    setLoading(true);

    try {
      const data: InterviewAnswerResult = await interviewAnswer(sessionId, userAnswer);

      setMessages((prev) => [
        ...prev,
        { role: "score", content: data.feedback, score: data.score, suggestions: data.suggestions },
      ]);

      if (data.is_complete) {
        setComplete(true);
      } else if (data.next_question) {
        setMessages((prev) => [...prev, { role: "interviewer", content: data.next_question }]);
      }
    } catch {
      setMessages((prev) => [...prev, { role: "interviewer", content: "评估失败，请重试。" }]);
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setStarted(false);
    setComplete(false);
    setSessionId(null);
    setMessages([]);
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">AI 模拟面试</h1>

      {!started ? (
        /* ---------- Setup ---------- */
        <div className="space-y-4">
          <p className="text-gray-500">填写 JD，AI 面试官将进行针对性模拟面试</p>
          <div>
            <label className="mb-1 block text-sm font-medium">目标岗位 JD *</label>
            <textarea
              className="h-32 w-full rounded-lg border p-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="粘贴职位描述..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
            />
          </div>
          <div>
            <div className="mb-1 flex items-center justify-between">
              <label className="text-sm font-medium">简历（可选）</label>
              <FileUploader onFile={setAttachedFile} />
            </div>
            <textarea
              className="h-24 w-full rounded-lg border p-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="粘贴简历文本或上传文件..."
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium">题目数量</label>
            <select
              className="rounded-lg border px-3 py-1.5 text-sm"
              value={total}
              onChange={(e) => setTotal(Number(e.target.value))}
            >
              {[3, 5, 7, 10].map((n) => (
                <option key={n} value={n}>{n} 题</option>
              ))}
            </select>
            <button
              onClick={handleStart}
              disabled={loading || !jdText.trim()}
              className="rounded-lg bg-blue-600 px-6 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "启动中..." : "开始面试"}
            </button>
          </div>
        </div>
      ) : (
        /* ---------- Chat ---------- */
        <div className="rounded-xl border bg-white shadow-sm">
          <div className="flex items-center justify-between border-b px-5 py-3">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">AI</div>
              <span className="text-sm font-medium">AI 面试官</span>
            </div>
            <button onClick={handleReset} className="text-xs text-gray-400 hover:text-red-500">结束面试</button>
          </div>

          <div className="h-[500px] space-y-4 overflow-y-auto p-5">
            {messages.map((msg, i) => {
              if (msg.role === "interviewer") {
                return (
                  <div key={i} className="flex gap-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-600">AI</div>
                    <div className="max-w-[80%] rounded-2xl rounded-tl-none bg-gray-100 px-4 py-3 text-sm whitespace-pre-wrap">{msg.content}</div>
                  </div>
                );
              }
              if (msg.role === "user") {
                return (
                  <div key={i} className="flex justify-end gap-3">
                    <div className="max-w-[80%] rounded-2xl rounded-tr-none bg-blue-600 px-4 py-3 text-sm whitespace-pre-wrap text-white">{msg.content}</div>
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-300 text-sm font-bold text-gray-600">U</div>
                  </div>
                );
              }
              if (msg.role === "score") {
                return (
                  <div key={i} className="rounded-xl border border-yellow-200 bg-yellow-50 px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold text-yellow-700">{msg.score}/10</span>
                      <span className="text-xs text-yellow-600">评分</span>
                    </div>
                    <p className="mt-1 text-sm text-gray-700">{msg.content}</p>
                    {msg.suggestions && msg.suggestions.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {msg.suggestions.map((s, j) => (
                          <li key={j} className="flex gap-1 text-xs text-yellow-800"><span>+</span> {s}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                );
              }
              return null;
            })}
            <div ref={chatEndRef} />
          </div>

          {!complete && (
            <div className="flex gap-3 border-t p-4">
              <input
                type="text"
                className="flex-1 rounded-lg border px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                placeholder="输入你的回答..."
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSubmitAnswer()}
                disabled={loading}
              />
              <button
                onClick={handleSubmitAnswer}
                disabled={loading || !answer.trim()}
                className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                发送
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
