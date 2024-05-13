FROM python:latest

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["python", "qbfastapi.py"]