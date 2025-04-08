FROM python:3.12-alpine

WORKDIR /app

RUN ["pip", "install", "--no-cache-dir", "alembic", "sqlalchemy", "python-dotenv", "psycopg2-binary"]

COPY /alembic /app/alembic
COPY models.py /app
COPY alembic.ini /app
COPY .env /app

ENTRYPOINT ["alembic", "upgrade", "head"]