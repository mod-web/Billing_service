FROM python:3.9
RUN apt-get update -y
RUN apt-get upgrade -y

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

RUN chmod +x run_uwsgi.sh

EXPOSE 8000

ENTRYPOINT ["/app/run_uwsgi.sh"]