FROM python:3.12
LABEL authors="cabup"

WORKDIR /app

RUN ["pip", "install", "poetry", "flask", "redis", "sqlalchemy", "jinja2", "requests", "python-dotenv", "psycopg2"]

COPY *.py /app/
COPY templates /app/templates
COPY .env /app/

ENTRYPOINT ["python", "main.py"]