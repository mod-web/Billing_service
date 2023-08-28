FROM --platform=linux/amd64 python:3.11-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -U setuptools pip \
     && pip install -r requirements.txt

EXPOSE 8000

COPY . .

RUN chmod +x run.sh
CMD ["/app/run.sh"]
