# Multi-stage build for CyberSentinel AI

# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend
COPY cybersentinel-dashboard/package*.json ./
RUN npm ci
COPY cybersentinel-dashboard/ ./
RUN npm run build

# Stage 2: Backend with Python
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt api_requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r api_requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY src/ ./src/
COPY models/ ./models/

# Copy frontend build
COPY --from=frontend-build /app/frontend/dist/cybersentinel-dashboard/browser ./frontend/dist

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/api/health || exit 1

# Start backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
