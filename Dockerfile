FROM node:24-bookworm-slim AS frontend
WORKDIR /app/web
ENV NEXT_TELEMETRY_DISABLED=1
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build && npm prune --omit=dev

FROM python:3.14-slim-bookworm
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 NEXT_TELEMETRY_DISABLED=1 NODE_ENV=production HUMBERTITO_REQUIRE_POSTGRES=1 HUMBERTITO_SECURE_COOKIES=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libstdc++6 && rm -rf /var/lib/apt/lists/* \
    && mkdir /app/data && chown 10001:10001 /app/data
COPY --from=frontend /usr/local/bin/node /usr/local/bin/node
COPY requirements.txt requirements-web.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt -r requirements-web.txt
COPY backend/ ./backend/
COPY --chown=10001:10001 --from=frontend /app/web/.next/ ./web/.next/
COPY --from=frontend /app/web/public/ ./web/public/
COPY --from=frontend /app/web/node_modules/ ./web/node_modules/
COPY --from=frontend /app/web/package.json /app/web/next.config.mjs ./web/
COPY scripts/run_cloud.py ./scripts/run_cloud.py
USER 10001:10001
CMD ["python", "scripts/run_cloud.py"]
