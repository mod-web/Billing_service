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

ENTRYPOINT ["gunicorn"]
CMD ["-b", "0.0.0.0:8001", "-w", "4", "-k", "uvicorn.workers.UvicornH11Worker", "main:app"]
