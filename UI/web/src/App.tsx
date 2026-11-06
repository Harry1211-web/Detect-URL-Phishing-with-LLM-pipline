import { useEffect, useRef, useState } from "react";
import { analyzeUrl, ERROR_MESSAGES, ScanError } from "./api/client";
import Header from "./components/Header";
import ResultCard, { LayerRail } from "./components/ResultCard";
import SampleUrls from "./components/SampleUrls";
import UrlScanner from "./components/UrlScanner";
import { MAX_URL_LENGTH } from "./config";
import type { AnalyzeResult } from "./types/api";

export default function App() {
  const [url, setUrl] = useState("");
  const [explain, setExplain] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState("");
  const outcome = useRef<HTMLDivElement>(null);

  // Brings the rail and the verdict into view on a projector-sized screen
  useEffect(() => {
    if (result) outcome.current?.scrollIntoView({ block: "start" });
  }, [result]);

  async function scan() {
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

  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <section className="mx-auto max-w-4xl px-4 pt-10 pb-12 sm:pt-16">
          <h1 className="font-display text-5xl font-extrabold tracking-tight text-balance sm:text-7xl">
            Can you trust this link?
          </h1>
          <p className="mt-4 text-lg text-muted sm:text-xl">
            Paste a link here before you open it or enter any information.
          </p>
          <UrlScanner
            url={url}
            explain={explain}
            loading={loading}
            onUrlChange={setUrl}
            onExplainChange={setExplain}
            onSubmit={scan}
          />
          {error && (
            <p role="alert" className="mt-4 border-l-4 border-phishing pl-3 font-semibold">
              {error}
            </p>
          )}
          <SampleUrls disabled={loading} onPick={setUrl} />
        </section>
        <div ref={outcome} className="scroll-mt-2">
          <div className="border-y border-line bg-surface">
            <LayerRail loading={loading} result={result} />
          </div>
          {result && (
            <div className="pt-8">
              <ResultCard key={result.url} result={result} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
