interface Props {
  explanation: string;
  decidedBy: string;
  latencyMs: number | null;
}

// The explanation may come from an LLM that read an attacker's page: plain text children only
export default function ExplanationBox({ explanation, decidedBy, latencyMs }: Props) {
  return (
    <details open className="mt-7 border-t border-line pt-5">
      <summary className="cursor-pointer font-semibold">View details</summary>
      <p className="mt-3 max-w-prose text-lg whitespace-pre-wrap">
        {explanation || "No further explanation is available for this result."}
      </p>
      <p className="mt-3 text-sm text-muted">
        Decided by {decidedBy || "unknown"}
        {latencyMs !== null && `, in ${Math.round(latencyMs)} ms`}
      </p>
    </details>
  );
}
