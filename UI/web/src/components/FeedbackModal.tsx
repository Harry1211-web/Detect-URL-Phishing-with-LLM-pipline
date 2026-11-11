import { useEffect, useRef, useState } from "react";
import { ERROR_MESSAGES, ScanError, sendFeedback } from "../api/client";
import { feedbackLabelFor } from "../lib/verdict";
import type { Verdict } from "../types/api";

interface Props {
  url: string;
  verdict: Verdict;
  onClose: () => void;
}

export default function FeedbackModal({ url, verdict, onClose }: Props) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [state, setState] = useState<"idle" | "sending" | "sent">("idle");
  const [error, setError] = useState("");
  const label = feedbackLabelFor(verdict);

  useEffect(() => {
    if (!dialog.current?.open) dialog.current?.showModal();
  }, []);

  async function submit() {
    setState("sending");
    setError("");
    try {
      await sendFeedback(url, label);
      setState("sent");
    } catch (err) {
      setState("idle");
      setError(ERROR_MESSAGES[err instanceof ScanError ? err.kind : "unavailable"]);
    }
  }

  return (
    <dialog
      ref={dialog}
      onClose={onClose}
      className="m-auto w-[min(28rem,calc(100vw-2rem))] rounded-md bg-surface p-6 text-ink backdrop:bg-black/60"
    >
      {state === "sent" ? (
        <>
          <h3 className="text-xl font-extrabold">Report sent</h3>
          <p className="mt-2 text-muted">This report helps the system judge links more accurately.</p>
          <button type="button" onClick={onClose} className="mt-5 rounded-md bg-ink px-4 py-2 font-semibold text-paper">
            Close
          </button>
        </>
      ) : (
        <>
          <h3 className="text-xl font-extrabold">
            {label === "phishing" ? "Report this link as phishing?" : "Report this link as safe?"}
          </h3>
          <p className="mt-2 font-mono text-sm break-all text-muted">{url}</p>
          {error && (
            <p role="alert" className="mt-3 font-semibold">
              {error}
            </p>
          )}
          <div className="mt-5 flex gap-2">
            <button
              type="button"
              disabled={state === "sending"}
              onClick={submit}
              className="rounded-md bg-ink px-4 py-2 font-semibold text-paper disabled:opacity-60"
            >
              Send report
            </button>
            <button type="button" onClick={onClose} className="rounded-md border-2 border-line px-4 py-2 font-semibold">
              Cancel
            </button>
          </div>
        </>
      )}
    </dialog>
  );
}
