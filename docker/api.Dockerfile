FROM python:3.12-slim

WORKDIR /code

COPY backend /code/backend

ENV PYTHONPATH=/code/backend

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg[binary] \
    pydantic

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]