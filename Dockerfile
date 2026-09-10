FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock* ./
RUN pip install --upgrade pip && pip install pipenv && pipenv install --deploy --ignore-pipfile

COPY src/ ./src
COPY .env.example ./

RUN mkdir -p logs

RUN useradd -m botuser
USER botuser

CMD ["python", "-m", "src.main"]
