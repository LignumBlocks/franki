FROM python:3.11-slim

WORKDIR /app

RUN pip install python-telegram-bot==13.15 requests

COPY . .

CMD ["python", "telegram_agent.py"]
