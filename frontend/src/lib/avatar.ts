// UI Avatars — 根据名称自动生成头像，无需上传
export function getAvatarUrl(name: string | undefined | null): string {
  const displayName = name || "User";
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=6366f1&color=fff&size=128&bold=true`;
}

// Gravatar fallback
export function getGravatarUrl(email: string | undefined | null, size = 128): string {
  if (!email) return getAvatarUrl("U");
  // Simple hash function for demo — production should use crypto.subtle
  const hash = btoa(email.trim().toLowerCase()).substring(0, 16);
  return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=identicon`;
}
