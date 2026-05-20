"use client";

import { useState, useEffect } from "react";
import RequireAuth from "@/lib/RequireAuth";
import { useAuth } from "@/lib/AuthProvider";
import { createClient } from "@/lib/supabaseClient";
import { getAvatarUrl } from "@/lib/avatar";
import { apiPost } from "@/lib/api";

export default function SettingsPage() {
  return <RequireAuth><SettingsContent /></RequireAuth>;
}

function SettingsContent() {
  const { user } = useAuth();
  const supabase = createClient();
  const [nickname, setNickname] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "ok" | "err"; text: string } | null>(null);

  useEffect(() => {
    if (user) {
      // Get nickname from Supabase user metadata
      const meta = user.user_metadata as { nickname?: string } | undefined;
      setNickname(meta?.nickname || user.email?.split("@")[0] || "");
    }
  }, [user]);

  async function handleSaveProfile() {
    setSaving(true);
    setMessage(null);
    try {
      // Update nickname in Supabase Auth metadata
      await supabase.auth.updateUser({ data: { nickname } });
      // Also update in backend user_profiles
      await apiPost("/user/profile", { nickname });
      setMessage({ type: "ok", text: "资料已保存" });
    } catch (e) {
      setMessage({ type: "err", text: e instanceof Error ? e.message : "保存失败" });
    } finally {
      setSaving(false);
    }
  }

  async function handleChangePassword() {
    if (!newPassword || newPassword.length < 6) {
      setMessage({ type: "err", text: "密码至少 6 位" });
      return;
    }
    setSaving(true);
    setMessage(null);
    try {
      await supabase.auth.updateUser({ password: newPassword });
      setNewPassword("");
      setMessage({ type: "ok", text: "密码已更新" });
    } catch (e) {
      setMessage({ type: "err", text: e instanceof Error ? e.message : "修改失败" });
    } finally {
      setSaving(false);
    }
  }

  if (!user) return null;

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold">账户设置</h1>
        <p className="mt-1 text-gray-500">管理你的个人信息和密码</p>
      </div>

      {/* Avatar & basic info */}
      <div className="rounded-2xl border bg-white p-6 shadow-sm">
        <h3 className="mb-4 font-semibold text-gray-800">个人信息</h3>
        <div className="flex items-center gap-5">
          <img
            src={getAvatarUrl(nickname)}
            alt="avatar"
            className="h-16 w-16 rounded-full ring-2 ring-indigo-100"
          />
          <div className="space-y-1">
            <p className="font-medium text-gray-900">{nickname || user.email}</p>
            <p className="text-sm text-gray-400">{user.email}</p>
          </div>
        </div>
        <div className="mt-4">
          <label className="mb-1 block text-sm font-medium text-gray-700">昵称</label>
          <input
            className="w-full rounded-lg border px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            placeholder="你的昵称"
          />
        </div>
        <button
          onClick={handleSaveProfile}
          disabled={saving}
          className="mt-4 rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          保存资料
        </button>
      </div>

      {/* Password */}
      <div className="rounded-2xl border bg-white p-6 shadow-sm">
        <h3 className="mb-4 font-semibold text-gray-800">修改密码</h3>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">新密码</label>
          <input
            type="password"
            className="w-full rounded-lg border px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="至少 6 位"
          />
        </div>
        <button
          onClick={handleChangePassword}
          disabled={saving}
          className="mt-4 rounded-lg bg-gray-700 px-5 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
        >
          更新密码
        </button>
      </div>

      {message && (
        <div className={`rounded-xl p-4 text-sm ${message.type === "ok" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-600"}`}>
          {message.text}
        </div>
      )}
    </div>
  );
}
