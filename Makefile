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

clear:
	$(COMPOSE) down -v

down:
	$(COMPOSE) down

stop:
	docker stop vuejs_container

start:
	docker vuejs_container
# 	@echo Access to https://"$(USER)".42.fr

reup: down up

clean:
	$(COMPOSE) down -v
# 	sudo rm -rf $(DATA_DIR)

fclean: clean
	docker system prune --all --force

cleardatabase: fclean
	docker volume rm ready2roll_pg_data

enterdb:
	@docker exec -it postgre_db psql -U r2r_admin -d ready2roll

re: fclean up

.PHONY: all up down stop start reup clean fclean enterdb re
