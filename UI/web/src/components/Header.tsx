import { useEffect, useState } from "react";
import { checkHealth } from "../api/client";
import { HEALTH_POLL_MS } from "../config";

export default function Header() {
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let active = true;
    const refresh = () => checkHealth().then((ok) => active && setOnline(ok));
    refresh();
    const timer = setInterval(refresh, HEALTH_POLL_MS);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, []);

  const status =
    online === null
      ? { text: "Connecting", dot: "bg-line" }
      : online
        ? { text: "Ready", dot: "bg-clean" }
        : { text: "Disconnected", dot: "bg-phishing" };

  return (
    <header className="mx-auto flex max-w-4xl items-center justify-between px-4 pt-5">
      <div className="flex items-center gap-2 font-display text-xl font-bold">
        <img src="/favicon.png" alt="" className="size-8" />
        PhishGuard
      </div>
      <p className="flex items-center gap-2 text-sm text-muted" role="status">
        <span className={`size-2.5 rounded-full ${status.dot}`} aria-hidden="true" />
        {status.text}
      </p>
    </header>
  );
}
