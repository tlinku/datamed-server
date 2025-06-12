# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
FROM --platform=$TARGETPLATFORM node:18-alpine AS production
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/build /app/build
RUN mkdir -p /app/build
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /app
USER appuser
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD wget -q -O- http://localhost:3000 || exit 1

CMD ["serve", "-s", "build", "-l", "3000"]
