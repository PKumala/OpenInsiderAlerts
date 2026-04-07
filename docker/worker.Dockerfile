FROM python:3.12-slim

WORKDIR /code

COPY backend /code/backend

ENV PYTHONPATH=/code/backend

RUN pip install --no-cache-dir \
    sqlalchemy \
    psycopg[binary] \
    apscheduler \
    requests \
    beautifulsoup4

CMD ["python", "-m", "app.scheduler.worker"]
