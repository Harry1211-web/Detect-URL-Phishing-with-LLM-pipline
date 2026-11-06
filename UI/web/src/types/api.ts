export type Verdict = "clean" | "suspicious" | "phishing";

export interface AnalyzeResult {
  url: string;
  verdict: Verdict;
  decided_by: string;
  explanation: string;
  latency_ms: number | null;
}

export type FeedbackLabel = "clean" | "phishing";

export type ErrorKind =
  | "forbidden"
  | "tooLong"
  | "invalid"
  | "rateMinute"
  | "rateDay"
  | "timeout"
  | "network"
  | "unavailable";
