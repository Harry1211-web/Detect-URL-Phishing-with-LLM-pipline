export interface UrlParts {
  before: string; // scheme and any user-info, e.g. "https://bank.com@"
  host: string; // the host the browser would really connect to
  after: string; // path, query, fragment
}

// Splits a URL for display. The URL parser returns the punycode host, which exposes look-alike
// characters, and treats "bank.com@evil.com" as host evil.com. Null when it cannot be parsed.
export function splitUrl(raw: string): UrlParts | null {
  try {
    const u = new URL(/^[a-z][a-z0-9+.-]*:\/\//i.test(raw) ? raw : `http://${raw}`);
    const auth = u.username ? `${u.username}${u.password ? `:${u.password}` : ""}@` : "";
    return { before: `${u.protocol}//${auth}`, host: u.host, after: `${u.pathname}${u.search}${u.hash}` };
  } catch {
    return null;
  }
}
