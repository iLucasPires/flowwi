#------------------------------------------------------------------------------
# BUILDER
#------------------------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  UV_CACHE_DIR=/root/.cache/uv

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv venv /opt/venv && \
  uv sync --frozen --no-dev --python /opt/venv/bin/python && \
  rm -rf "$UV_CACHE_DIR"

#------------------------------------------------------------------------------
# DEV
#------------------------------------------------------------------------------
FROM python:3.12-slim AS dev

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  UV_CACHE_DIR=/root/.cache/uv \
  VIRTUAL_ENV=/opt/venv \
  PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv venv /opt/venv && \
  uv sync --frozen --python /opt/venv/bin/python && \
  rm -rf "$UV_CACHE_DIR"

COPY . .

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

##------------------------------------------------------------------------------
# PROD
#------------------------------------------------------------------------------
FROM python:3.12-slim AS prod

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  VIRTUAL_ENV=/opt/venv \
  PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv


# Copia apenas o necessário para rodar
COPY manage.py ./
COPY server/ ./server/
COPY app/ ./app/
COPY app/ ./app/
COPY locale/ ./locale/
COPY script/ ./script/

RUN chmod +x script/*.sh

EXPOSE 8000

CMD ["sh", "script/run.sh"]
