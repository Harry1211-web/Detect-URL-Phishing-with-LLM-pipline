// The only backend the UI may call; the detection API itself stays private
export const BFF_URL: string = import.meta.env.VITE_BFF_URL ?? "http://localhost:8080";

// Slightly above the BFF upstream timeout (40 s), so its 504 arrives first
export const ANALYZE_TIMEOUT_MS = 45_000;
export const HEALTH_POLL_MS = 30_000;
export const MAX_URL_LENGTH = 4096;
