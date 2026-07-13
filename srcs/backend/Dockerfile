# syntax=docker/dockerfile:1

# ==========================================
# FASE 1: BUILDER
# ==========================================
FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Creiamo l'ambiente virtuale FUORI dalla cartella /app (in /opt/venv)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# FASE 2: SVILUPPO
# ==========================================
FROM builder AS development

# Attiviamo l'ambiente virtuale corretto
ENV PATH="/opt/venv/bin:$PATH"

COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ==========================================
# FASE 3: PRODUZIONE
# ==========================================
FROM python:3.10-slim AS production

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copiamo l'ambiente virtuale dal builder alla nuova posizione
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

EXPOSE 8000
CMD ["gunicorn", "myapp.wsgi:application", "--bind", "0.0.0.0:8000"]
