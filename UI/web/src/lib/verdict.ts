import type { FeedbackLabel, Verdict } from "../types/api";

// Anything unexpected is shown as a warning: the UI must never fail towards "safe"
export function normalizeVerdict(value: unknown): Verdict {
  return value === "clean" || value === "phishing" ? value : "suspicious";
}

// A report always contradicts the verdict shown
export function feedbackLabelFor(verdict: Verdict): FeedbackLabel {
  return verdict === "clean" ? "phishing" : "clean";
}

export const VERDICT_COPY: Record<Verdict, { title: string; advice: string }> = {
  phishing: {
    title: "This is a phishing page",
    advice: "Do not open this link or enter passwords, OTP codes or card details.",
  },
  suspicious: {
    title: "This page is suspicious",
    advice:
      "There is not enough evidence to decide. Open the link only if you know the sender, and do not enter personal information.",
  },
  clean: {
    title: "No signs of phishing found",
    advice: "Still check the domain below carefully before entering personal information.",
  },
};

export type LayerId = "A" | "B" | "C" | "D";

export const LAYERS: { id: LayerId; name: string; hint: string }[] = [
  { id: "A", name: "Blocklist", hint: "Known phishing feeds" },
  { id: "B", name: "Look-alike check", hint: "Misspelled brand names" },
  { id: "C", name: "URL model", hint: "BiLSTM and XGBoost" },
  { id: "D", name: "Page reading", hint: "An LLM reads the page" },
];

export interface LayerTrace {
  decider: LayerId;
  reached: LayerId; // Last layer known to have contributed
  caption: string;
}

// Fallbacks stop at C: Layer D was off or gave no usable answer. Unknown values claim nothing
export function layerTrace(decidedBy: string): LayerTrace | null {
  if (decidedBy === "A_blocklist") {
    return { decider: "A", reached: "A", caption: "This link is on a phishing blocklist." };
  }
  if (decidedBy === "verified_official_domain") {
    return { decider: "A", reached: "A", caption: "This domain is on the verified official list." };
  }
  if (decidedBy === "C_classifier") {
    return { decider: "C", reached: "C", caption: "The URL model cleared this link." };
  }
  if (decidedBy === "D_llm") {
    return { decider: "D", reached: "D", caption: "The LLM read the page and made the final call." };
  }
  if (decidedBy.startsWith("D_llm+")) {
    return { decider: "D", reached: "D", caption: "The LLM read the page, but another warning still applies." };
  }
  if (decidedBy === "fallback_B") {
    return { decider: "B", reached: "C", caption: "The look-alike check decided, without an LLM reading of the page." };
  }
  if (decidedBy === "fallback_C") {
    return { decider: "C", reached: "C", caption: "The URL model decided, without an LLM reading of the page." };
  }
  return null;
}
