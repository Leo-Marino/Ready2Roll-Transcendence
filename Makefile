COMPOSE = docker compose -f compose.yaml

DATA_DIR = /sgoinfre/$(USER)/ready2roll

all: down up #setup

setup:
	@mkdir -p /sgoinfre/$(USER)/ready2roll
	@mkdir -p $(DATA_DIR)/pg_data
	@mkdir -p $(DATA_DIR)/minio_data
	@mkdir -p $(DATA_DIR)/redis_data

up: setup
	$(COMPOSE) build --parallel
	$(COMPOSE) up 
# 	@echo Access to https://"$(USER)".42.fr

clear:
	$(COMPOSE) down -v
	rm -rf $(DATA_DIR)

down:
	$(COMPOSE) down
# -v cancella volumi?

stop:
	docker stop vuejs_container

start:
	docker vuejs_container
# 	@echo Access to https://"$(USER)".42.fr

reup: down up

clean: down
# 	sudo rm -rf $(DATA_DIR)

fclean: clean
	docker system prune --all --force

cleardatabase: fclean
	docker volume rm ready2roll_pg_data

enterdb:
	@docker exec -it ready2roll-db psql -U r2r_admin -d ready2roll

re: fclean up
