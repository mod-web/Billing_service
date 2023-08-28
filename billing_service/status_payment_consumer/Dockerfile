FROM --platform=linux/amd64 python:3.11-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
     && pip install --upgrade pip

COPY requirements.txt requirements.txt
COPY . .

RUN pip install -r requirements.txt --no-cache-dir

CMD python main.py