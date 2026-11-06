# Run Guide

This guide takes you from a new computer to a running PhishGuard. It takes about 15 minutes, most of it
waiting for the first download. You do not need Python or Node.js.

You will do this once:

1. Install the tools and download the code.
2. Create the `.env` settings file.

Then, every time you want to use the system:

3. Start it with one command.
4. Check a link.
5. Stop it.

## 1. Install the tools and download the code

Install these three tools first:

| Tool | Why you need it | Where to get it |
|---|---|---|
| Docker Desktop | Runs the whole system | <https://www.docker.com/products/docker-desktop/> |
| Git | Downloads the code | <https://git-scm.com/downloads> |
| Google Chrome or Microsoft Edge | Shows the desktop window | Usually installed already |

Open Docker Desktop and wait until it says it is running. Leave it open.

Open a terminal (PowerShell on Windows, Terminal on macOS) and run:

```bash
git clone https://github.com/Harry1211-web/Dectect-URL-Phishing-with-LLM-pipline.git
cd Dectect-URL-Phishing-with-LLM-pipline
git checkout kha
```

Run every command in this guide from this folder.

## 2. Create the `.env` file

`.env` holds your private settings. It stays on your computer: never upload it or send it to anyone.

**Step 1. Make a random secret.** Run the line for your system and copy the result.

| System | Command |
|---|---|
| Windows | `[guid]::NewGuid().ToString("N")` |
| macOS | `openssl rand -hex 24` |

**Step 2. Open a new `.env` file.**

| System | Command |
|---|---|
| Windows | `notepad .env` (choose Yes when it asks to create the file) |
| macOS | `nano .env` |

**Step 3. Paste this, then fill in the first two lines.**

```ini
API_KEY=paste-the-random-secret-here
OPENAI_API_KEY=paste-your-openai-key-here
FE_ORIGINS=http://localhost:5173
API_EXPOSE_LAYERS=0
BFF_RATE_PER_MIN=60
BFF_RATE_PER_DAY=1000
```

**Step 4. Save and close the file.** On macOS with nano, press `Ctrl+O`, `Enter`, then `Ctrl+X`.

Three rules prevent most problems:

- Do not put spaces around `=`.
- Keep `FE_ORIGINS` exactly as shown. `*` does not work.
- The file name is `.env`, not `.env.txt`.

**No OpenAI key?** Delete the `OPENAI_API_KEY` line and add `USE_LLM=0`. The system still runs, but it cannot
read web pages, so hard links come back as `suspicious`.

The LLM stops at a spending limit of $1.40 by default. To change it, add a line such as `LLM_BUDGET_USD=5`.

## 3. Start the system

Make sure Docker Desktop is running, then run:

| System | Command |
|---|---|
| Windows | `.\start.cmd` |
| macOS | `sh start.sh` (not tested on macOS yet) |

The first start takes several minutes because it downloads and builds everything. Later starts are much faster.

When it finishes, a small desktop window opens and the terminal prints:

```text
PhishGuard is running.
  Web UI:  http://localhost:5173
  Stop:    docker compose down
```

Open <http://localhost:5173> in your browser for the full web app. Always use `localhost`, not `127.0.0.1`.

On the very first start, wait a few more minutes before you judge any results. The phishing feeds and the Tranco
list are still downloading in the background.

## 4. Check a link

Paste a link into the desktop window or the web app, then press **Check link**. Tick **AI** in the desktop window,
or **Include an AI explanation (slower)** in the web app, if you want an explanation from the LLM.

Try these three inputs to confirm that everything works:

| Input | Expected result |
|---|---|
| `https://www.vietcombank.com.vn/` | Green: "No signs of phishing found" |
| `http://vietcombamk-xacthuc.com/login` | Red: "This is a phishing page" |
| `javascript:alert(1)` | An error message, no result |

## 5. Stop the system

Close the desktop window, then run:

```bash
docker compose down
```

To use the system again, go back to section 3.

## 6. If something goes wrong

| What you see | What it means | What to do |
|---|---|---|
| `Missing .env file` | `.env` does not exist in this folder | Do section 2. On Windows, check that it is not named `.env.txt` |
| `Docker is not running` | Docker Desktop is closed or still starting | Open it, wait until it is ready, then start again |
| `API_KEY must be set` or `FE_ORIGINS must be set` | A line is missing from `.env` | Check the file against section 2 |
| The web app shows "Disconnected" | The backend is down, or the address is wrong | Open the app through `localhost`, check `FE_ORIGINS`, then run `docker compose ps` |
| `The detection service did not start` | The API failed or is still loading | Wait one minute and start again. If it repeats, run `docker compose logs api` |
| `Chrome or Edge was not found` | No browser for the desktop window | Install one, or use the web app link |
| Port 5173 or 8080 is already in use | Another program uses the port | Close that program, then start again |
| Many results are `suspicious` | The LLM is off or out of budget, or the page could not be downloaded | Check `OPENAI_API_KEY`, `USE_LLM` and `LLM_BUDGET_USD` |
| "Too many requests" | You reached the rate limit | Raise `BFF_RATE_PER_MIN`, then run `docker compose up -d bff` |
| `updater` shows `unhealthy` in `docker compose ps` | Harmless: it reuses the API health check but has no web server | Nothing to do |
| `data/blocklist/` shows as changed in git | The updater refreshed the feeds | Normal. Do not commit it unless you want the new snapshot |

After you change `.env`, run `docker compose up -d` so that the new values take effect.

## 7. For developers

Run the backend tests in the API image:

```bash
docker run --rm --user root -v "${PWD}/tests:/app/tests:ro" -v "${PWD}/bff:/app/bff:ro" -v "${PWD}/data:/app/data:ro" phishing-api sh -c "pip install -q pytest pytest-asyncio && python -m pytest tests/test_bff.py tests/test_api.py -q -p no:cacheprovider"
```

To work on the UI, install Node.js 22.12 or newer. The dev server uses the same port as the `ui` container, so
stop that container first:

```bash
docker compose stop ui
cd UI/web
npm install
npm run dev
```
