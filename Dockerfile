FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock* ./
RUN pip install --upgrade pip && pip install pipenv && pipenv install --system --deploy --ignore-pipfile

COPY src/ ./src
COPY .env.example ./

RUN useradd -u 1001 -r -g 0 -m -d /app botuser && \
    mkdir -p /app/logs && \
    chown -R 1001:0 /app && \
    chmod -R g=u /app

USER 1001

CMD ["python", "-m", "src.main"]