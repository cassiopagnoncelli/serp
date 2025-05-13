FROM python:3.13-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

# Create app directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock ./

# Configure poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies without dev dependencies and without installing the root project
RUN poetry install --only main --no-interaction --no-ansi --no-root

# Final stage
FROM python:3.13-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    curl \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Install poetry in the final image for console script
RUN pip install --no-cache-dir poetry

# Create app directory
WORKDIR /app

# Create non-root user and setup home directory properly
RUN groupadd -r appuser && useradd -r -g appuser -m appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /home/appuser/.cache && \
    chown -R appuser:appuser /home/appuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Setup bash aliases for appuser
RUN cp /app/.bash_aliases /home/appuser/.bash_aliases && \
    echo 'if [ -f ~/.bash_aliases ]; then . ~/.bash_aliases; fi' >> /home/appuser/.bashrc && \
    echo 'export PATH="/app/bin:$PATH"' >> /home/appuser/.bashrc && \
    chown appuser:appuser /home/appuser/.bash_aliases /home/appuser/.bashrc

# Give execute permission to the console script
RUN chmod +x /app/bin/console

# Remove unnecessary files from the final image
RUN rm -f /app/.bash_aliases /app/.dockerignore /app/.gitignore /app/Dockerfile /app/Makefile

# Configure poetry to create virtualenvs in the appuser's home directory
USER appuser
RUN poetry config virtualenvs.path /home/appuser/.cache/pypoetry/virtualenvs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/home/appuser \
    PYTHONPATH=/app \
    PATH="/app/bin:${PATH}"

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
