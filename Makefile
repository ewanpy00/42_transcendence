COMPOSE = docker compose

up:
	$(COMPOSE) up -d --build

ps:
	$(COMPOSE) ps

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

.PHONY: up ps down logs