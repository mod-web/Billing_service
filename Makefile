#!make

# Get env
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Fill table type_subscribe
fill:
	docker-compose exec billing_postgres psql -h 127.0.0.1 -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f /fill.sql
