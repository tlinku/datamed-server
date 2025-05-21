# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM node:18-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code and build
COPY . .
RUN npm run build

# Production stage
FROM --platform=$TARGETPLATFORM node:18-alpine AS production

WORKDIR /app

# Install serve for production
RUN npm install -g serve

# Copy built app from builder stage
COPY --from=builder /app/build /app/build

# Create a directory for serve to use (in case the build directory wasn't copied correctly)
RUN mkdir -p /app/build

# Use non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD wget -q -O- http://localhost:3000 || exit 1

CMD ["serve", "-s", "build", "-l", "3000"]
