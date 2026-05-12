FROM python:3.12
LABEL authors="cabup"

WORKDIR /app

RUN ["pip3", "install", "poetry", "flask", "redis", "sqlalchemy", "jinja2", "requests", "python-dotenv", "psycopg2", "poetry"]
COPY ./pyproject.toml /app/
RUN ["poetry", "install"]
COPY *.py /app/
COPY templates /app/templates
COPY .env /app/

ENTRYPOINT ["python3", "main.py"]