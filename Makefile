COMPOSE = docker compose

DATA_DIR = /sgoinfre/$(USER)/ready2roll

export PUBLIC_HOST_IP  := $(shell hostname -I | awk '{print $$1}')
export PUBLIC_HOSTNAME := $(shell hostname -f 2>/dev/null || hostname)

all: down up

vault-status:
	$(COMPOSE) exec vault vault status

keygen: # 1. Initialize vault and create token keys
	$(COMPOSE) exec vault vault operator init -key-shares=5 -key-threshold=3

unseal: # 2. Unseal vault
	$(COMPOSE) exec vault vault operator unseal
	$(COMPOSE) exec vault vault operator unseal
	$(COMPOSE) exec vault vault login
	docker compose restart vault-agent

enable:	# 3. Run only once per initialization
	docker compose exec vault vault audit enable file file_path=/vault/logs/audit.log
	docker compose exec vault vault secrets enable -path=r2r kv-v2
	printf 'path "r2r/data/django" {\n  capabilities = ["read"]\n}\n' | \
	    docker compose exec -T vault vault policy write django-read -
	docker compose exec vault vault auth enable approle
	docker compose exec vault vault write auth/approle/role/django token_policies=django-read token_ttl=1h token_max_ttl=4h
	mkdir -p secrets/approle
	docker compose exec -T vault vault read -field=role_id auth/approle/role/django/role-id > secrets/approle/role_id
	docker compose exec -T vault vault write -f -field=secret_id auth/approle/role/django/secret-id > secrets/approle/secret_id

loadsecrets: # 4. Load secrets in vault
	$(COMPOSE) exec -T vault vault kv put r2r/django - < ./r2r-secrets.json
#	shred -u ./r2r-secrets.json

setup:
	@mkdir -p $(DATA_DIR)/pg_data
	@mkdir -p $(DATA_DIR)/minio_data
	@mkdir -p $(DATA_DIR)redis_data
	@export UID GID=$(id -g)

up: setup
	$(COMPOSE) build --parallel
	$(COMPOSE) up -d
	@echo "login at https://localhost:8443/login"

run-app: up # Runs a script to automatically unseal vault
	chmod +x vault-bootstrap.sh
	./vault-bootstrap.sh

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

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


start:
	docker vuejs_container

save-database:
	@docker compose exec django sh -c 'set -a; . /vault/secrets/django.env; set +a; python manage.py dumpdata' > srcs/backend/demo_data.json
	@echo "Database has been saved! You are ready to roll!"

restore-database:
	@docker compose exec django sh -c \
    	'set -a; . /vault/secrets/django.env; set +a; python manage.py loaddata demo_data.json'
	@echo "Database is restored. You are ready to roll!"

save-media:
	@echo "Compressing MinIO media..."
	@tar -czvf media_backup.tar.gz -C /sgoinfre/$(USER)/ready2roll/minio_data media/
	@echo "Backup complete! You can now upload media_backup.tar.gz to Google Drive."

restore-media: setup
	@echo "Restoring MinIO media..."
	@tar -xzvf media_backup.tar.gz -C /sgoinfre/$(USER)/ready2roll/minio_data
	@echo "Media restored successfully!"

save-all: save-database save-media

restore-all: restore-database restore-media

reup: down up

clean:
	$(COMPOSE) down -v

fclean: clean
	docker system prune --all --force
	@rm -rf secrets/vault-init.json

cleardatabase: fclean
	docker volume rm ready2roll_pg_data

re: fclean up

.PHONY: all up down restart clean fclean re keygen unseal enable loadsecrets run-app
