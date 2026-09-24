#!/bin/sh
set -e

# Semeia status iniciais e o administrador (idempotente).
# Falha aqui é intencional: o sistema não deve subir sem admin inicial.
python seed_admin.py

exec uvicorn app.main:app --host 0.0.0.0 --port 8050
