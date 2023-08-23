FROM python:3.10-slim-buster

WORKDIR app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -U setuptools pip \
     && pip install -r requirements.txt

EXPOSE 5000

COPY . .

CMD python3 -m flask --app --reload --host=0.0.0.0
