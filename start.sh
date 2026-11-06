#!/bin/sh
# Starts the system on macOS: Docker services, then the desktop window
cd "$(dirname "$0")" || exit 1
WEB_URL=http://localhost:5173
DESKTOP_URL=$WEB_URL/desktop.html

if [ ! -f .env ]; then
  echo "Missing .env file. See section 2 of RUNGUIDE.md."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Open Docker Desktop, wait until it is ready, then run this again."
  exit 1
fi

echo "Starting PhishGuard. The first run takes several minutes."
docker compose up -d --build || exit 1

echo "Waiting for the detection service..."
ready=0
i=0
while [ "$i" -lt 60 ]; do
  if curl -fs http://localhost:8080/api/health 2>/dev/null | grep -q true; then
    ready=1
    break
  fi
  i=$((i + 1))
  sleep 2
done
if [ "$ready" -ne 1 ]; then
  echo "The detection service did not start. Check it with: docker compose logs api"
  exit 1
fi

# A separate profile always opens a new window, whatever browser windows are already open
opened=0
for app in "Google Chrome" "Microsoft Edge"; do
  if [ -d "/Applications/$app.app" ]; then
    open -na "$app" --args --app="$DESKTOP_URL" --window-size=580,100 \
      --user-data-dir="$HOME/Library/Application Support/PhishGuard/browser" \
      --no-first-run --no-default-browser-check
    opened=1
    break
  fi
done
if [ "$opened" -ne 1 ]; then
  echo "Chrome or Edge was not found, so the desktop window cannot open."
fi

echo
echo "PhishGuard is running."
echo "  Web UI:  $WEB_URL"
echo "  Stop:    docker compose down"
