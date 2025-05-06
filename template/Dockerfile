FROM python:3.13

ENV PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_NO_INTERACTION=1

WORKDIR /app/

# System-level operations (as root)
RUN apt-get update && apt-get install -y \
    locales \
    vim \
    nano \
    curl \
    wget \
    imagemagick
RUN locale-gen en_US.UTF-8

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en

# Install latest Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry --version && \
    poetry self update

# Create non-root user
RUN useradd -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# Set up user-specific bash configuration
COPY --chown=appuser:appuser .bash_aliases /home/appuser/.bash_aliases
RUN echo "if [ -f ~/.bash_aliases ]; then" >> /home/appuser/.bashrc && \
    echo "    . ~/.bash_aliases" >> /home/appuser/.bashrc && \
    echo "fi" >> /home/appuser/.bashrc

# Switch to non-root user for application setup
USER appuser
WORKDIR /app

# User-level environment setup
ENV POETRY_HOME="/home/appuser/.local" \
    PATH="/home/appuser/.local/bin:$PATH"

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml poetry.lock* ./

# Install dependencies with caching
RUN poetry install --no-interaction --no-cache

ENV PYTHONPATH=/app

# Copy application files
COPY --chown=appuser:appuser . /app/

# Install the project
RUN poetry install --no-root --no-interaction

CMD ["poetry", "run", "fastapi", "run", "--workers", "8", "app/server.py"]
