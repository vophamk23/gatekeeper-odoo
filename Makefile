# Makefile for Odoo t4_gatekeeper development

# Variables
COMPOSE_FILE = docker/docker-compose.yml
ODOO_SERVICE = odoo
DB_SERVICE = postgres
DB_NAME = gatekeeper_db

.PHONY: help up down restart status logs upgrade shell db-shell test test-api

help:
	@echo "Available commands:"
	@echo "  make up        - Start containers in background"
	@echo "  make down      - Stop and remove containers"
	@echo "  make restart   - Restart Odoo container"
	@echo "  make status    - Show container status"
	@echo "  make logs      - View Odoo logs (follow)"
	@echo "  make upgrade   - Upgrade t4_gate_keeper module"
	@echo "  make shell     - Open Odoo shell inside container"
	@echo "  make db-shell  - Open PostgreSQL terminal inside container"
	@echo "  make test      - Run automated Odoo tests for t4_gate_keeper"
	@echo "  make test-api  - Run integration API HTTP client tests on localhost:8070"

up:
	docker compose -f $(COMPOSE_FILE) up -d

down:
	docker compose -f $(COMPOSE_FILE) down

restart:
	docker compose -f $(COMPOSE_FILE) restart $(ODOO_SERVICE)

status:
	docker compose -f $(COMPOSE_FILE) ps

logs:
	docker compose -f $(COMPOSE_FILE) logs -f --tail=100 $(ODOO_SERVICE)

upgrade:
	docker compose -f $(COMPOSE_FILE) exec $(ODOO_SERVICE) odoo -d $(DB_NAME) -u t4_gate_keeper --stop-after-init
	docker compose -f $(COMPOSE_FILE) restart $(ODOO_SERVICE)

shell:
	docker compose -f $(COMPOSE_FILE) exec $(ODOO_SERVICE) odoo shell -d $(DB_NAME)

db-shell:
	docker compose -f $(COMPOSE_FILE) exec $(DB_SERVICE) psql -U odoo -d $(DB_NAME)

test:
	docker compose -f $(COMPOSE_FILE) exec $(ODOO_SERVICE) odoo -d $(DB_NAME) -i t4_gate_keeper --test-enable --stop-after-init --http-port 8073

test-api:
	python utils/test_api_client.py
