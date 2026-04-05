# UHAKIX Frontend — Next.js
FROM node:20-alpine AS builder

WORKDIR /app

# Install deps
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# Build args
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Copy source
COPY frontend/ .

# Build
RUN npm run build

# ── Production ─────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# copy only what's needed for Next.js production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/.next/standalone ./

EXPOSE 3000

CMD ["node", "server.js"]
