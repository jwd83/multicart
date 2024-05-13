FROM python:latest

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn pygame-ce numpy requests

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "qbfastapi:app", "--host", "0.0.0.0"]