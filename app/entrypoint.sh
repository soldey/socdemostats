#!/bin/bash

alembic upgrade head
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
exec "$@"