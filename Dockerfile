FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_DIR=/app

# Non-root 1001:1001 (to match your seed user/group)
ARG PUID=1001
ARG PGID=1001
RUN groupadd -g ${PGID} appgroup \
 && useradd -m -u ${PUID} -g appgroup -s /bin/bash appuser

# Build tools for wheels (only what’s needed at runtime install)
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR $APP_DIR

# Startup script:
# - verifies /app (host bind) exists
# - installs deps to /app/.deps if needed (persistent)
# - exports PYTHONPATH to include /app and /app/.deps
# - runs bot + dashboard (gunicorn on 0.0.0.0:5000)
RUN printf '%s\n' \
  '#!/bin/sh' \
  'set -e' \
  'APP_DIR="${APP_DIR:-/app}"' \
  'DEPS_DIR="$APP_DIR/.deps"' \
  'REQS_FILE="$APP_DIR/requirements.txt"' \
  '' \
  'if [ ! -d "$APP_DIR" ]; then' \
  '  echo "[fatal] $APP_DIR not mounted from host" >&2; exit 1' \
  'fi' \
  'mkdir -p "$DEPS_DIR" "$APP_DIR/logs" "$APP_DIR/data"' \
  '' \
  '# Install/refresh deps if requirements.txt present' \
  'if [ -f "$REQS_FILE" ]; then' \
  '  REQS_HASH_FILE="$DEPS_DIR/.requirements.sha256"' \
  '  NEW_HASH=$(sha256sum "$REQS_FILE" | cut -d" " -f1)' \
  '  OLD_HASH=$(cat "$REQS_HASH_FILE" 2>/dev/null || true)' \
  '  if [ "$NEW_HASH" != "$OLD_HASH" ]; then' \
  '    echo "[deps] installing/updating Python packages to $DEPS_DIR"' \
  '    pip install --no-cache-dir -r "$REQS_FILE" --target "$DEPS_DIR"' \
  '    echo "$NEW_HASH" > "$REQS_HASH_FILE"' \
  '  fi' \
  'fi' \
  '' \
  'export PYTHONPATH="$APP_DIR:$DEPS_DIR:$PYTHONPATH"' \
  'export PATH="$DEPS_DIR/bin:$PATH"' \
  '' \
  'cd "$APP_DIR"' \
  'echo "[init] running DB migration..."' \
  'python scripts/init_database.py || true' \
  '' \
  'echo "[start] launching bot (main.py)..."' \
  'python main.py & BOT_PID=$!' \
  '' \
  'echo "[start] launching dashboard (gunicorn) on 0.0.0.0:5000..."' \
  'exec python -m gunicorn "src.api.api_server:app" -b 0.0.0.0:5000 --workers 1 --threads 1 --timeout ${GUNICORN_TIMEOUT:-120}' \
  > /usr/local/bin/start-hostapp.sh \
 && chmod +x /usr/local/bin/start-hostapp.sh

USER appuser

# Ensure data directory exists before DB init
RUN mkdir -p "$APP_DIR/data"

EXPOSE 5000
ENTRYPOINT ["/usr/local/bin/start-hostapp.sh"]
