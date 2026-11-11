import { describe, expect, it } from "vitest";
import { splitUrl } from "./urlParts";
import { feedbackLabelFor, layerTrace, normalizeVerdict } from "./verdict";

describe("verdicts", () => {
  it("keeps known verdicts and turns the rest into suspicious", () => {
    expect(normalizeVerdict("clean")).toBe("clean");
    expect(normalizeVerdict("phishing")).toBe("phishing");
    for (const other of ["suspicious", "safe", "", null, undefined, 1]) {
      expect(normalizeVerdict(other)).toBe("suspicious");
    }
  });

  it("reports the opposite of the verdict shown", () => {
    expect(feedbackLabelFor("clean")).toBe("phishing");
    expect(feedbackLabelFor("suspicious")).toBe("clean");
    expect(feedbackLabelFor("phishing")).toBe("clean");
  });
});

describe("layerTrace", () => {
  it.each([
    ["A_blocklist", "A", "A"],
    ["verified_official_domain", "A", "A"],
    ["C_classifier", "C", "C"],
    ["D_llm", "D", "D"],
    ["D_llm+evasion", "D", "D"],
    ["D_llm+C_override", "D", "D"],
    ["fallback_B", "B", "C"],
    ["fallback_C", "C", "C"],
  ])("maps %s to its layers", (decidedBy, decider, reached) => {
    expect(layerTrace(decidedBy)).toMatchObject({ decider, reached });
  });

  it.each(["", "fallback_lookup_failed", "something_new"])("claims no layer for %j", (decidedBy) => {
    expect(layerTrace(decidedBy)).toBeNull();
  });
});

describe("splitUrl", () => {
  it("exposes the real host behind a user-info trick", () => {
    expect(splitUrl("https://vietcombank.com.vn@evil.com/login")).toEqual({
      before: "https://vietcombank.com.vn@",
      host: "evil.com",
      after: "/login",
    });
  });

  it("shows look-alike characters as punycode", () => {
    expect(splitUrl("https://vietcombаnk.com/")?.host).toMatch(/^xn--/);
  });

  it("accepts a bare domain", () => {
    expect(splitUrl("example.com:8080/a")?.host).toBe("example.com:8080");
  });

  it("returns null when the URL cannot be parsed", () => {
    expect(splitUrl("http://")).toBeNull();
  });
});
