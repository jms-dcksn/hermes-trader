# Stage 1: Node build
FROM node:20-slim AS frontend-build

WORKDIR /app

# Copy frontend files
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.12-slim AS backend

WORKDIR /app

# Install uv for Python dependency management
RUN pip install uv

# Copy backend files
COPY backend/pyproject.toml backend/uv.lock* backend/README.md ./
RUN uv sync --frozen --no-dev

# Copy frontend build output
COPY --from=frontend-build /app/out ./static

# Copy backend application code
COPY backend/ ./

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]