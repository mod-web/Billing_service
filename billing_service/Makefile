#!make

# Get env
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

all: build_d fill

build:
	docker-compose up --build

build_d:
	docker-compose up --build -d

# Fill table type_subscribe
fill:
	echo "Waiting for init..."
	sleep 5
	docker-compose exec billing_postgres psql -h 127.0.0.1 -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f /fill.sql
	echo "Insert type_subscribes completed!"

