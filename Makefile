COMPOSE = docker compose -f compose.yaml

DATA_DIR = /sgoinfre/$(USER)/ready2roll

all: down up #setup

setup:
	@mkdir -p /sgoinfre/$(USER)/ready2roll
	@mkdir -p $(DATA_DIR)/pg_data
	@mkdir -p $(DATA_DIR)/minio_data

up: setup
	$(COMPOSE) build --parallel
	$(COMPOSE) up -d
# 	@echo Access to https://"$(USER)".42.fr


down:
	$(COMPOSE) down
# -v cancella volumi?

clear:
	$(COMPOSE) down -v
	rm -rf $(DATA_DIR)

migration-clean: clear
	@echo "Stopping containers..."
	@echo "Removing Postgres physical data..."
	@rm -rf $(DATA_DIR)/pg_data
	@echo "Cleaning django migrations..."
	@find srcs/backend -path "*/migrations/*.py" -not -name "__init__.py" -delete
	@find srcs/backend -path "*/migrations/*.pyc" -delete
	@find . -name "*.pyc" -delete
	@find srcs/backend -name "__pycache__" -type d -exec rm -rf {} +
	@echo "Database and migrations clean completed."

stop:
	docker stop vuejs_container

start:
	docker vuejs_container
# 	@echo Access to https://"$(USER)".42.fr

reup: down up

clean: down

fclean: clean
	docker system prune --all --force

cleardatabase: fclean
	docker volume rm ready2roll_pg_data

enterdb:
	@docker exec -it ready2roll-db psql -U r2r_admin -d ready2roll

re: fclean up
