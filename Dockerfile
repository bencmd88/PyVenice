# Multi-stage build for optimized PyVenice container
FROM python:3.12-alpine AS builder

# Install build dependencies for any compiled packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install PyVenice
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir pyvenice

# Production stage - minimal runtime image
FROM python:3.12-alpine

# Install only runtime dependencies
RUN apk add --no-cache \
    libssl3 \
    libffi \
    && rm -rf /var/cache/apk/*

# Copy the virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN adduser -D -s /bin/sh pyvenice
USER pyvenice

# Create working directory
WORKDIR /app

# Verify installation
RUN python -c "import pyvenice; print('PyVenice installed successfully')"

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python"]

# Metadata
LABEL maintainer="Kieran Bicheno <kieran@bicheno.me>"
LABEL description="PyVenice - A comprehensive Python client for the Venice.ai API"
LABEL version="0.1.0"
LABEL org.opencontainers.image.source="https://github.com/TheLustriVA/PyVenice"
LABEL org.opencontainers.image.documentation="https://github.com/TheLustriVA/PyVenice#readme"
LABEL org.opencontainers.image.licenses="MIT"