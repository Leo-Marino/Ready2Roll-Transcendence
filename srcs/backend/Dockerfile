# syntax=docker/dockerfile:1

# ==========================================
# FASE 1: BUILDER
# ==========================================
FROM python:3.10-slim AS builder

# Evita la scrittura di file .pyc e forza l'output immediato dei log
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Creiamo un ambiente virtuale (best practice anche con pip)
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copiamo SOLO la lista della spesa per sfruttare la cache di Docker
COPY requirements.txt .

# Installiamo tutte le librerie
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# FASE 2: SVILUPPO (Per testare sul tuo PC)
# ==========================================
FROM builder AS development

# Attiviamo l'ambiente virtuale
ENV PATH="/app/.venv/bin:$PATH"

# Copiamo tutto il codice del progetto
COPY . .
EXPOSE 8000

# Server di sviluppo base di Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ==========================================
# FASE 3: PRODUZIONE (Per la valutazione finale)
# ==========================================
FROM python:3.10-slim AS production

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copiamo SOLO l'ambiente virtuale già pronto dalla fase builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copiamo il codice sorgente
COPY . .

EXPOSE 8000

# Lanciamo Gunicorn, lo standard per la produzione
CMD ["gunicorn", "myapp.wsgi:application", "--bind", "0.0.0.0:8000"]