// Shared type definitions for the AI Job Assistant frontend

export interface SkillGap {
  skill: string;
  importance: "required" | "preferred" | "bonus";
}

export interface JDAnalysisResult {
  match_score: number;
  match_summary: string;
  core_overlap: string[];
  missing_skills: SkillGap[];
  strength_analysis: string;
  gap_analysis: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface InterviewSession {
  session_id: string;
  messages: ChatMessage[];
  topic: string;
}
