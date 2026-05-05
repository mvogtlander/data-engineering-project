FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml only (no data files!)
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv sync --no-dev --frozen

# Copy the ingestion script
COPY ./01-docker-terraform/ingestion.py .

# Create output directory for logs/exports
RUN mkdir -p /app/output

CMD ["uv", "run", "python", "ingestion.py"]