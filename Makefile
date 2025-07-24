.PHONY: up down build logs bash freq backtest train

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose build

bash:
	docker compose exec freqtrade bash

freq:
	docker compose exec freqtrade freqtrade $(ARGS)

backtest:
	docker compose exec freqtrade freqtrade backtesting --config user_data/config.json --strategy ema_super $(ARGS)

train:
	docker compose exec freqtrade freqtrade freqai-train --config user_data/config.json --strategy ema_super $(ARGS)
