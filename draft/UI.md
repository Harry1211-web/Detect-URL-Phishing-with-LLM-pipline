# UI IMPLEMENTATION GUIDE FOR CLAUDE CODE
> **Document Purpose:** Detailed technical specification and implementation guide for building two user interfaces (**Web Scanner Dashboard** and **Compact Desktop Window**) that integrate with the Phishing Detection Pipeline via Backend-for-Frontend (BFF).

---

## 1. Architecture & Core Principles

```
┌─────────────────────────┐          ┌──────────────────────────────────┐
│  1. Web Application     │          │  2. Desktop Window               │
│  (localhost:5173/)      │          │  (localhost:5173/desktop.html)   │
└────────────┬────────────┘          └────────────────┬─────────────────┘
             │ Origin: http://localhost:5173          │ Same origin
             └───────────────────────┬────────────────┘
                                     │ HTTPS / HTTP POST
                                     ▼
                     ┌───────────────────────────────┐
                     │   Backend-for-Frontend (BFF)  │ (Port 8080)
                     │   bff/app.py                  │ Abuse controls: CORS,
                     │                               │ Rate limit (10/min, 300/day)
                     └───────────────┬───────────────┘
                                     │ Private Docker Network + X-API-Key
                                     ▼
                     ┌───────────────────────────────┐
                     │   Core Detection API          │ (Port 8000)
                     │   src/api.py                  │
                     │   (Layers A -> B -> C -> D)   │
                     └───────────────────────────────┘
```

### Golden Rules for Claude Code
1. **Never call the core API (`src/api.py`, port 8000) directly:** FE must **only** communicate with the **BFF** (`http://localhost:8080`).
2. **No API keys on the client:** The FE does not possess or store any secrets/API keys. The BFF handles upstream authentication server-side.
3. **Strict XSS Defense (Crucial):** Never render the API's `explanation` field as HTML (no `innerHTML`, no `dangerouslySetInnerHTML`). Attackers can manipulate page content to inject malicious scripts into LLM summaries. **Always render plain text.**
4. **Never make scanned URLs clickable:** Do not render `<a href="...">` for a scanned URL, whatever the verdict. Show it as text; there is no "continue to site" button.
   **Never fail towards safe:** an unknown or missing `verdict` is shown as `suspicious`, and an error never keeps the color of an earlier result.
5. **Origin Matching:** The BFF enforces strict `FE_ORIGINS` checks. The FE origin must be listed in the backend's `.env` under `FE_ORIGINS`.

---

## 2. API Contract Specification (BFF Endpoints)

Base URL in development: `http://localhost:8080`

### 2.1 Analyze URL: `POST /api/analyze`
* **Headers:**
  - `Content-Type: application/json`
  - `Origin: <FE_ORIGIN>` (Automatically sent by browsers)
  - `X-Turnstile-Token: <token>` (*Optional*, only if Cloudflare Turnstile is enabled in BFF)

* **Request Body:**
```json
{
  "url": "https://vietcombamk-xacthuc.com/login",
  "explain": true,
  "lang": "en"
}
```
| Field | Type | Required | Description |
|---|---|---|---|
| `url` | string | Yes | Target URL to check (max 4096 chars). Accepts `http://`, `https://`, or bare domains (`example.com`). |
| `explain` | boolean | No (default `false`) | `true` requests an AI-generated natural language explanation (requires Layer D LLM). |
| `lang` | string | No (default `"vi"`) | ISO language code (`vi`, `en`, `zh`, `ja`, etc.). Default Vietnamese. |

* **Response (HTTP 200 OK):**
```json
{
  "url": "https://vietcombamk-xacthuc.com/login",
  "verdict": "phishing",
  "decided_by": "fallback_B",
  "explanation": "Label 'vietcombamkxacthuc' — small misspelling of the brand name: ...",
  "latency_ms": 242.3
}
```

* **Verdict Mappings for UI:**
| `verdict` | Meaning | UI State / Color | Recommended UI Action |
|---|---|---|---|
| `clean` | No phishing signs found | 🟢 Green | Say no signs were found; do not promise the page is safe. |
| `suspicious` | High risk / Inconclusive | 🟠 Orange | Warn the user; advise against entering personal data. |
| `phishing` | Confirmed malicious | 🔴 Red | Strong danger alert; discourage visiting entirely. |

* **HTTP Error Handling:**
| HTTP Code | Cause | User-Facing Message |
|---|---|---|
| `403` | Origin not allowed or Turnstile failed | "Request refused. Reload the page and try again." |
| `413` | Body > 16 KB (a URL of 4097 chars up to 16 KB returns `422`, so the FE checks the length first) | "This link is too long. The maximum is 4096 characters." |
| `422` | Invalid URL format (e.g. `javascript:alert(1)`) | "Invalid link. Enter a website link starting with http or https." |
| `429` | Exceeded rate limit (10/min or 300/day; `detail` starts with `Daily` for the day limit) | "Too many requests. Try again in 1 minute." or, for the day limit, "You have used all of today's checks. Try again tomorrow." |
| `502` / `503` | Backend/API offline or misconfigured | "The checking service is unavailable. Try again later." |
| `504` | Analysis timeout (> 40s) | "The check took too long. Try again." |
| No response | Network failure, or a refused CORS preflight (the browser hides the status, so a web app never sees the `403` for a wrong origin) | "Could not reach the checking service. Check your network connection and try again." |
| Client timeout | No answer after 45 s | Same message as `504` |

The `422` body has a list in `detail`; other errors have a string. Choose messages from the status. `HUONG_DAN_FE.md` is the full API reference.

**`explanation`:** a fixed English sentence, except when `decided_by` starts with `D_llm` and `explain` is `true`. Both UIs are in English and always send `lang: "en"`, so `explanation` is in English too. The web app shows `explanation` and `decided_by` under "View details".

### 2.2 User Feedback: `POST /api/feedback`
Used for false-positive / false-negative reporting.
* **Request Body:**
```json
{
  "url": "https://example.com",
  "label": "clean"
}
```
* `label`: `"clean"` (if safe site was wrongly flagged) or `"phishing"` (if phishing site was missed).
* **Response:** `{"ok": true}`

### 2.3 Service Health: `GET /api/health`
* **Response:** `{"ok": true}` (or `{"ok": false}`)
* Use to show system readiness pill (`🟢 Online` / `🔴 Offline`) on UI header.

---

## 3. Implementation: UI 1 - Web Application (Web Scanner)

### 3.1 Tech Stack
* **Framework:** React + Vite + TypeScript.
* **Styling:** Tailwind CSS v4 through `@tailwindcss/vite` (no `tailwind.config.js`), always light so it stays bright on a projector.
* **Fonts:** Bricolage Grotesque for headings, Be Vietnam Pro for text, and JetBrains Mono with ligatures off for URLs; all bundled, no CDN.
* **Icons:** lucide-react.

### 3.2 Directory Structure
```text
UI/web/
├── index.html, package.json, vite.config.ts, tsconfig.json
├── public/favicon.png
└── src/
    ├── main.tsx, App.tsx, index.css
    ├── config.ts              # BFF base URL (VITE_BFF_URL), timeouts, limits
    ├── api/client.ts          # Fetch wrappers for /api/analyze, /feedback, /health; error mapping
    ├── lib/verdict.ts         # Verdict normalization and English copy
    ├── lib/urlParts.ts        # Splits a URL to expose its real host
    ├── components/            # Header, UrlScanner, ResultCard, ExplanationBox, FeedbackModal, SampleUrls
    └── types/api.ts           # TypeScript interfaces for API contracts
```

### 3.3 Result Display
`ResultCard` shows the URL as text with the real host highlighted. The URL parser reveals user-info tricks
(`bank.com@evil.com`) and returns punycode for look-alike characters.

### 3.4 Key UI States to Handle
1. **Idle:** Ready for user input. Show quick sample buttons:
   - Sample Clean: `https://www.vietcombank.com.vn/`
   - Sample Phishing: `http://vietcombamk-xacthuc.com/login`
   - Sample hidden domain: `https://vietcombank.com.vn@example.com/login`
2. **Loading:** Lock submit button, display spinner and textual state ("Checking through 4 layers of protection...").
3. **Success:** Display `ResultCard` matching verdict:
   - Green (`clean`): Checkmark icon, "No signs of phishing found".
   - Orange (`suspicious`): Alert triangle icon, "This page is suspicious".
   - Red (`phishing`): Shield alert icon, "This is a phishing page".
   - Show `explanation`, `decided_by` and `latency_ms` under "View details".
4. **Error:** Display toast or alert with friendly message mapping from Section 2.

`LayerRail` (in `ResultCard.tsx`) always shows Layers A to D. `layerTrace` in `lib/verdict.ts` maps `decided_by` to the deciding layer; an unknown value marks no layer. While scanning the rail only pulses: the API reports no progress.

---

## 4. Implementation: UI 2 - Desktop Window

### 4.1 How it Works
* `UI/web/desktop.html` and `src/desktop.tsx` are a second page of the web project. They share the API client, verdict copy and URL display with the web app.
* The `ui` container serves both pages. Docker cannot open a window on the host, so `start.cmd` (Windows) and `start.sh` (macOS) open the page in Chrome or Edge app mode, without browser toolbars.
* The launcher uses its own browser profile, so a new window opens even when the browser is already running.

### 4.2 Layout
* One bar: link input, "AI" checkbox (Include an AI explanation, slower) and "Check link".
* Nothing else shows until a check ends. The verdict, the URL with its real domain highlighted and the explanation then appear under the bar.
* The window resizes to its content with `window.resizeTo`. A normal browser tab ignores this call.

---

## 5. Backend Configuration Required for FE

`RUNGUIDE.md` covers setup, including `.env`. The FE origins must be listed exactly:

```ini
FE_ORIGINS=http://localhost:5173
```

The BFF does not load `.env` by itself: Docker Compose passes the values in. Outside Docker, set `API_URL`,
`API_KEY` and `FE_ORIGINS` as environment variables.

---

## 6. Verification Checklist

1. `npm test` and `npm run build` pass in `UI/web`.
2. `GET /api/health` returns `{"ok": true}`.
3. A clean URL, a phishing URL and `javascript:alert(1)` give the results listed in `RUNGUIDE.md`.
4. No `innerHTML` or `dangerouslySetInnerHTML`, and no `<a>` for a scanned URL.
5. An error after a clean result is neutral, not green. An unknown verdict is shown as `suspicious`.
