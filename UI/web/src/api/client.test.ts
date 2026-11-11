import { afterEach, describe, expect, it, vi } from "vitest";
import { analyzeUrl, checkHealth, ScanError } from "./client";

function stubResponse(status: number, body: unknown) {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(body), { status })));
}

async function kindOf(promise: Promise<unknown>) {
  const err = await promise.catch((e) => e);
  expect(err).toBeInstanceOf(ScanError);
  return (err as ScanError).kind;
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("analyzeUrl", () => {
  it("asks for the explanation in English", async () => {
    stubResponse(200, {});
    await analyzeUrl("http://a.com", true);
    const init = vi.mocked(fetch).mock.calls[0][1] as RequestInit;
    expect(JSON.parse(init.body as string).lang).toBe("en");
  });

  it("shows an unknown verdict as suspicious, never as clean", async () => {
    stubResponse(200, { url: "http://a.com", verdict: "maybe", decided_by: "x", explanation: "", latency_ms: 1 });
    expect((await analyzeUrl("http://a.com", true)).verdict).toBe("suspicious");
  });

  it("shows a missing verdict as suspicious", async () => {
    stubResponse(200, {});
    expect((await analyzeUrl("http://a.com", true)).verdict).toBe("suspicious");
  });

  it.each([
    [403, { detail: "Origin not allowed." }, "forbidden"],
    [413, { detail: "Request body too large." }, "tooLong"],
    [422, { detail: [{ msg: "bad" }] }, "invalid"],
    [429, { detail: "Too many requests, retry in a minute." }, "rateMinute"],
    [429, { detail: "Daily limit reached, try again tomorrow." }, "rateDay"],
    [502, { detail: "Analysis service error." }, "unavailable"],
    [503, { detail: "Server has no API_KEY configured." }, "unavailable"],
    [504, { detail: "The analysis took too long, try again." }, "timeout"],
  ])("maps HTTP %i to its error kind", async (status, body, kind) => {
    stubResponse(status, body);
    expect(await kindOf(analyzeUrl("http://a.com", true))).toBe(kind);
  });

  it("reports a blocked or failed request as a network error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    expect(await kindOf(analyzeUrl("http://a.com", true))).toBe("network");
  });

  it("reports a non-JSON success body as unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("<html>", { status: 200 })));
    expect(await kindOf(analyzeUrl("http://a.com", true))).toBe("unavailable");
  });

  it("aborts after the client timeout", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("fetch", vi.fn((_url: string, init: RequestInit) =>
      new Promise((_resolve, reject) => {
        init.signal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")));
      })));
    const pending = kindOf(analyzeUrl("http://a.com", true));
    await vi.advanceTimersByTimeAsync(45_000);
    expect(await pending).toBe("timeout");
  });
});

describe("checkHealth", () => {
  it("is false when the service is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    expect(await checkHealth()).toBe(false);
  });
});
