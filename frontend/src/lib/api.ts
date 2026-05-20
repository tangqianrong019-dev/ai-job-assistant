const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function apiGet(path: string) {
  const { createClient } = await import("./supabaseClient");
  const supabase = createClient();
  const { data: { session } } = await supabase.auth.getSession();

  const headers: Record<string, string> = {};
  if (session?.access_token) {
    headers["Authorization"] = `Bearer ${session.access_token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { headers });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json();
}

export async function apiPost<T = unknown>(path: string, body: T) {
  const { createClient } = await import("./supabaseClient");
  const supabase = createClient();
  const { data: { session } } = await supabase.auth.getSession();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (session?.access_token) {
    headers["Authorization"] = `Bearer ${session.access_token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg.includes("403") ? "免费次数已用完，请升级" : msg.includes("401") ? "请先登录" : `API ${res.status}: ${msg}`);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Typed wrappers
// ---------------------------------------------------------------------------

export interface JDMatchResult {
  match_percentage: number;
  match_summary: string;
  core_overlap: string[];
  missing_skills: { skill: string; importance: string }[];
  suggestions: string[];
}

export interface ResumeOptimizeResult {
  strength_discovery: string[];
  missing_skills: string[];
  rewritten_projects: { original: string; rewritten: string }[];
  summary: string;
}

export interface InterviewStartResult {
  session_id: string;
  question: string;
  question_number: number;
  total: number;
}

export interface InterviewAnswerResult {
  score: number;
  feedback: string;
  suggestions: string[];
  next_question: string;
  question_number: number;
  total: number;
  is_complete: boolean;
}

export interface ProjectGenResult {
  markdown: string;
}

export interface OfferScoreRow {
  company: string;
  salary_score: number;
  benefits_score: number;
  commute_score: number;
  growth_score: number;
  overall: number;
}

export interface OfferCompareResult {
  score_table: OfferScoreRow[];
  analysis: string;
}

export async function jdMatch(resumeText: string, jdText: string) {
  return apiPost<{ resume_text: string; jd_text: string }>("/jobs/match", {
    resume_text: resumeText,
    jd_text: jdText,
  }) as Promise<JDMatchResult>;
}

export async function resumeOptimize(resumeText: string, jdText: string) {
  return apiPost<{ resume_text: string; jd_text: string }>("/resume/optimize", {
    resume_text: resumeText,
    jd_text: jdText,
  }) as Promise<ResumeOptimizeResult>;
}

export async function interviewStart(jdText: string, resumeText = "", count = 5) {
  return apiPost("/interview/start", {
    jd_text: jdText,
    resume_text: resumeText,
    question_count: count,
  }) as Promise<InterviewStartResult>;
}

export async function interviewAnswer(sessionId: string, answer: string) {
  return apiPost("/interview/answer", {
    session_id: sessionId,
    answer,
  }) as Promise<InterviewAnswerResult>;
}

export async function projectGen(name: string, stack: string, achievements: string) {
  return apiPost("/project/generate", {
    project_name: name,
    tech_stack: stack,
    achievements,
  }) as Promise<ProjectGenResult>;
}

export async function offerCompare(offers: { company: string; salary: string; benefits: string; commute: string; growth: string }[]) {
  return apiPost("/offer/compare", { offers }) as Promise<OfferCompareResult>;
}
