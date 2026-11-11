import { LoaderCircle } from "lucide-react";
import { StrictMode, useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { createRoot } from "react-dom/client";
import { analyzeUrl, ERROR_MESSAGES, ScanError } from "./api/client";
import { UrlAnatomy, VERDICT_STYLE } from "./components/ResultCard";
import { MAX_URL_LENGTH } from "./config";
import { VERDICT_COPY } from "./lib/verdict";
import type { AnalyzeResult } from "./types/api";
import "./index.css";

// Fixed: passing outerWidth back to resizeTo makes the window a few pixels wider on every call
const WINDOW_WIDTH = 580;

// Fits the app window to its content; a normal browser tab ignores resizeTo
function fitWindow(contentHeight: number) {
  const frame = window.outerHeight - window.innerHeight;
  window.resizeTo(WINDOW_WIDTH, Math.min(contentHeight + frame, window.screen.availHeight));
}

function DesktopApp() {
  const root = useRef<HTMLDivElement>(null);
  const [url, setUrl] = useState("");
  const [explain, setExplain] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const element = root.current;
    if (!element) return;
    const observer = new ResizeObserver(() => fitWindow(element.offsetHeight));
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  async function scan(event: FormEvent) {
    event.preventDefault();
    if (loading) return;
    const target = url.trim();
    setResult(null);
    if (!target) return setError("Enter a link to check.");
    if (target.length > MAX_URL_LENGTH) return setError(ERROR_MESSAGES.tooLong);

    setError("");
    setLoading(true);
    try {
      setResult(await analyzeUrl(target, explain));
    } catch (err) {
      setError(ERROR_MESSAGES[err instanceof ScanError ? err.kind : "unavailable"]);
    } finally {
      setLoading(false);
    }
  }

  const style = result ? VERDICT_STYLE[result.verdict] : null;
  const copy = result ? VERDICT_COPY[result.verdict] : null;

  return (
    <div ref={root}>
      <form onSubmit={scan} className="flex items-center gap-2 bg-surface p-2" noValidate>
        <label htmlFor="target-url" className="sr-only">
          Link to check
        </label>
        <input
          id="target-url"
          type="text"
          inputMode="url"
          autoComplete="off"
          spellCheck={false}
          autoFocus
          placeholder="https://..."
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          className="min-w-0 flex-1 rounded-lg border-2 border-ink bg-surface px-3 py-2 font-mono text-sm text-ink placeholder:text-muted"
        />
        <label
          title="Include an AI explanation (slower)"
          className="flex shrink-0 cursor-pointer items-center gap-1.5 text-sm font-semibold"
        >
          <input
            type="checkbox"
            checked={explain}
            aria-label="Include an AI explanation (slower)"
            onChange={(event) => setExplain(event.target.checked)}
            className="size-4 accent-brand"
          />
          AI
        </label>
        <button
          type="submit"
          disabled={loading}
          className="flex shrink-0 items-center gap-1.5 rounded-lg bg-brand px-3 py-2 text-sm font-semibold text-white hover:bg-ink disabled:cursor-wait disabled:opacity-60"
        >
          {loading && <LoaderCircle className="size-4 animate-spin motion-reduce:animate-none" aria-hidden="true" />}
          {loading ? "Checking" : "Check link"}
        </button>
      </form>

      {error && (
        <p role="alert" className="border-t border-line bg-surface px-3 py-2 text-sm font-semibold">
          {error}
        </p>
      )}

      {result && style && copy && (
        <section aria-live="polite" className="bg-surface">
          <div className={`verdict-band ${style.band} flex items-start gap-2 px-3 py-2.5 text-white`}>
            <style.Icon className="mt-0.5 size-6 shrink-0" aria-hidden="true" />
            <div>
              <h1 className="font-display text-lg leading-tight font-extrabold">{copy.title}</h1>
              <p className="mt-0.5 text-sm">{copy.advice}</p>
            </div>
          </div>
          <div className="px-3 py-3">
            <UrlAnatomy url={result.url} compact />
            {/* The explanation may come from an LLM that read an attacker's page: plain text only */}
            <p className="mt-2 text-sm whitespace-pre-wrap">
              {result.explanation || "No further explanation is available for this result."}
            </p>
          </div>
        </section>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <DesktopApp />
  </StrictMode>,
);
