import { CircleCheck, ShieldAlert, TriangleAlert } from "lucide-react";
import { useState } from "react";
import { splitUrl } from "../lib/urlParts";
import { LAYERS, layerTrace, VERDICT_COPY } from "../lib/verdict";
import type { AnalyzeResult, Verdict } from "../types/api";
import ExplanationBox from "./ExplanationBox";
import FeedbackModal from "./FeedbackModal";

export const VERDICT_STYLE: Record<Verdict, { band: string; text: string; Icon: typeof CircleCheck }> = {
  clean: { band: "bg-clean", text: "text-clean", Icon: CircleCheck },
  suspicious: { band: "bg-suspicious", text: "text-suspicious", Icon: TriangleAlert },
  phishing: { band: "bg-phishing", text: "text-phishing", Icon: ShieldAlert },
};

// Shows the system's layers and, after a scan, which one decided
export function LayerRail({ loading, result }: { loading: boolean; result: AnalyzeResult | null }) {
  const trace = result ? layerTrace(result.decided_by) : null;
  const reached = trace ? LAYERS.findIndex((layer) => layer.id === trace.reached) : -1;
  const style = result ? VERDICT_STYLE[result.verdict] : null;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h2 className="font-display text-2xl font-bold tracking-tight">How each link is checked</h2>
      <ol className="mt-5 grid gap-6 sm:grid-cols-4 sm:gap-4">
        {LAYERS.map((layer, index) => {
          const decided = layer.id === trace?.decider;
          const dot = decided
            ? `${style?.band} border-transparent text-white`
            : index <= reached
              ? "border-transparent bg-brand text-white"
              : "border-line bg-surface text-muted";
          return (
            <li key={layer.id} className={`rail-stop flex gap-3 sm:block ${index < reached ? "is-passed" : ""}`}>
              <span
                className={`rail-dot grid size-11 shrink-0 place-items-center rounded-full border-2 font-display text-lg font-bold ${dot} ${loading ? "is-checking" : ""}`}
                style={loading ? { animationDelay: `${index * 200}ms` } : undefined}
                aria-hidden="true"
              >
                {layer.id}
              </span>
              <div className="sm:mt-3">
                <p className="font-semibold">{layer.name}</p>
                <p className="text-sm text-muted">{layer.hint}</p>
                {decided && <p className={`mt-1 text-sm font-extrabold ${style?.text}`}>Decided here</p>}
              </div>
            </li>
          );
        })}
      </ol>
      {trace && <p className="mt-5 font-semibold">{trace.caption}</p>}
    </div>
  );
}

// The URL is text on purpose: no result, whatever the verdict, renders a clickable link
export function UrlAnatomy({ url, compact = false }: { url: string; compact?: boolean }) {
  const parts = splitUrl(url);
  return (
    <p className={`font-mono break-all ${compact ? "text-sm" : "text-lg sm:text-xl"}`}>
      {parts ? (
        <>
          <span className="text-muted">{parts.before}</span>
          <strong className={`real-domain font-mono font-medium ${compact ? "text-base" : "text-2xl sm:text-3xl"}`}>
            {parts.host}
          </strong>
          <span className="text-muted">{parts.after}</span>
        </>
      ) : (
        url
      )}
    </p>
  );
}

export default function ResultCard({ result }: { result: AnalyzeResult }) {
  const [reporting, setReporting] = useState(false);
  const { band, Icon } = VERDICT_STYLE[result.verdict];
  const copy = VERDICT_COPY[result.verdict];

  return (
    <section aria-live="polite" className="mx-auto max-w-4xl px-4 pb-16">
      <div className="overflow-hidden rounded-2xl border border-line bg-surface">
        <div className={`verdict-band ${band} flex gap-4 px-6 py-7 text-white sm:px-10`}>
          <Icon className="size-12 shrink-0" aria-hidden="true" />
          <div>
            <h2 className="font-display text-3xl font-extrabold tracking-tight sm:text-5xl">{copy.title}</h2>
            <p className="mt-2 max-w-prose text-lg">{copy.advice}</p>
          </div>
        </div>
        <div className="px-6 py-7 sm:px-10">
          <UrlAnatomy url={result.url} />
          <p className="mt-3 text-sm text-muted">The highlighted part is the link's real domain.</p>
          <ExplanationBox
            explanation={result.explanation}
            decidedBy={result.decided_by}
            latencyMs={result.latency_ms}
          />
          <button
            type="button"
            onClick={() => setReporting(true)}
            className="mt-6 rounded-lg border-2 border-ink px-4 py-2 font-semibold hover:bg-paper"
          >
            Report wrong result
          </button>
        </div>
      </div>
      {reporting && (
        <FeedbackModal url={result.url} verdict={result.verdict} onClose={() => setReporting(false)} />
      )}
    </section>
  );
}
