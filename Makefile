COMPOSE = docker compose -f compose.yaml

DATA_DIR = ~/data

all: down up #setup

# setup:
# 	@mkdir -p $(DATA_DIR)/mariadb
# 	@mkdir -p $(DATA_DIR)/wordpress

up:
	$(COMPOSE) build --parallel
	$(COMPOSE) up -d
# 	@echo Access to https://"$(USER)".42.fr

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

enterdb:
	@docker exec -it ready2roll-db psql -U r2r_admin -d ready2roll

re: fclean up
