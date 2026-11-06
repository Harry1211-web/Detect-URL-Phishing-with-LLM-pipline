import { ANALYZE_TIMEOUT_MS, BFF_URL } from "../config";
import { normalizeVerdict } from "../lib/verdict";
import type { AnalyzeResult, ErrorKind, FeedbackLabel } from "../types/api";

export class ScanError extends Error {
  kind: ErrorKind;

  constructor(kind: ErrorKind) {
    super(kind);
    this.kind = kind;
  }
}

// Chosen from the HTTP status, never from raw server text
export const ERROR_MESSAGES: Record<ErrorKind, string> = {
  forbidden: "Request refused. Reload the page and try again.",
  tooLong: "This link is too long. The maximum is 4096 characters.",
  invalid: "Invalid link. Enter a website link starting with http or https.",
  rateMinute: "Too many requests. Try again in 1 minute.",
  rateDay: "You have used all of today's checks. Try again tomorrow.",
  timeout: "The check took too long. Try again.",
  network: "Could not reach the checking service. Check your network connection and try again.",
  unavailable: "The checking service is unavailable. Try again later.",
};

function kindFromStatus(status: number, detail: unknown): ErrorKind {
  switch (status) {
    case 403:
      return "forbidden";
    case 413:
      return "tooLong";
    case 422:
      return "invalid";
    case 429:
      return typeof detail === "string" && detail.startsWith("Daily") ? "rateDay" : "rateMinute";
    case 504:
      return "timeout";
    default:
      return "unavailable";
  }
}

async function post(path: string, body: unknown): Promise<unknown> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ANALYZE_TIMEOUT_MS);
  try {
    // A refused CORS preflight also lands in the catch: the browser hides the status from us
    const res = await fetch(`${BFF_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new ScanError(kindFromStatus(res.status, data?.detail));
    }
    return await res.json();
  } catch (err) {
    if (err instanceof ScanError) throw err;
    if (controller.signal.aborted) throw new ScanError("timeout");
    throw new ScanError(err instanceof SyntaxError ? "unavailable" : "network");
  } finally {
    clearTimeout(timer);
  }
}

export async function analyzeUrl(url: string, explain: boolean, lang = "en"): Promise<AnalyzeResult> {
  const data = (await post("/api/analyze", { url, explain, lang })) as Partial<AnalyzeResult>;
  return {
    url: typeof data.url === "string" ? data.url : url,
    verdict: normalizeVerdict(data.verdict),
    decided_by: typeof data.decided_by === "string" ? data.decided_by : "",
    explanation: typeof data.explanation === "string" ? data.explanation : "",
    latency_ms: typeof data.latency_ms === "number" ? data.latency_ms : null,
  };
}

export async function sendFeedback(url: string, label: FeedbackLabel): Promise<void> {
  await post("/api/feedback", { url, label });
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BFF_URL}/api/health`);
    const data = await res.json();
    return res.ok && data?.ok === true;
  } catch {
    return false;
  }
}
