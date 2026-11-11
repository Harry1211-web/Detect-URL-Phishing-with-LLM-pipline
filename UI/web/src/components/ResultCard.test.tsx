import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { Verdict } from "../types/api";
import ResultCard from "./ResultCard";

const PAYLOAD = '<img src=x onerror=alert(1)><a href="http://evil.com">click</a>';

function render(verdict: Verdict) {
  return renderToStaticMarkup(
    <ResultCard
      result={{ url: "http://evil.com/login", verdict, decided_by: "D_llm", explanation: PAYLOAD, latency_ms: 12 }}
    />,
  );
}

describe("ResultCard", () => {
  it.each<Verdict>(["clean", "suspicious", "phishing"])("renders no link and no raw HTML for %s", (verdict) => {
    const html = render(verdict);
    expect(html).not.toContain("<a");
    expect(html).not.toContain("<img");
    expect(html).toContain("&lt;img");
  });
});
