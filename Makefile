COMPOSE = docker compose

up:
	$(COMPOSE) up -d

ps:
	$(COMPOSE) ps

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

.PHONY: up ps down logs