import { Link2, LoaderCircle } from "lucide-react";
import type { FormEvent } from "react";

interface Props {
  url: string;
  explain: boolean;
  loading: boolean;
  onUrlChange: (value: string) => void;
  onExplainChange: (value: boolean) => void;
  onSubmit: () => void;
}

export default function UrlScanner({ url, explain, loading, onUrlChange, onExplainChange, onSubmit }: Props) {
  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!loading) onSubmit();
  }

  return (
    <form onSubmit={handleSubmit} className="mt-8" noValidate>
      <label htmlFor="target-url" className="sr-only">
        Link to check
      </label>
      <div className="address-bar flex flex-col gap-2 rounded-2xl border-[3px] border-ink bg-surface p-2 sm:flex-row sm:items-center">
        <Link2 className="ml-3 hidden size-6 shrink-0 text-muted sm:block" aria-hidden="true" />
        <input
          id="target-url"
          type="text"
          inputMode="url"
          autoComplete="off"
          spellCheck={false}
          placeholder="https://..."
          value={url}
          onChange={(event) => onUrlChange(event.target.value)}
          className="min-w-0 flex-1 bg-transparent px-3 py-3 font-mono text-lg text-ink placeholder:text-muted sm:text-xl"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-xl bg-brand px-7 py-3.5 text-lg font-semibold text-white hover:bg-ink disabled:cursor-wait disabled:opacity-60"
        >
          Check link
        </button>
      </div>
      <label className="mt-3 flex items-center gap-2 text-sm text-muted">
        <input
          type="checkbox"
          checked={explain}
          onChange={(event) => onExplainChange(event.target.checked)}
          className="size-4 accent-brand"
        />
        Include an AI explanation (slower)
      </label>
      {loading && (
        <p role="status" className="mt-4 flex items-center gap-2 font-semibold">
          <LoaderCircle className="size-5 animate-spin motion-reduce:animate-none" aria-hidden="true" />
          Checking through 4 layers of protection...
        </p>
      )}
    </form>
  );
}
