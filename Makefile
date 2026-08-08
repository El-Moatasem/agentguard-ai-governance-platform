.PHONY: api web install-api install-web migrate migration test build docker docker-down seed clean

install-api:
	cd apps/api && python -m pip install -r requirements.txt

install-web:
	cd apps/web && yarn install --frozen-lockfile

migrate:
	cd apps/api && alembic upgrade head

migration:
	cd apps/api && alembic revision --autogenerate -m "$(name)"

api:
	cd apps/api && alembic upgrade head && uvicorn app.main:app --reload

web:
	cd apps/web && yarn dev

test:
	cd apps/api && pytest -q

build:
	cd apps/web && yarn build

docker:
	docker compose up --build

docker-down:
	docker compose down

seed:
	cd apps/api && python ../../scripts/seed_demo_data.py

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf apps/api/.pytest_cache apps/web/dist
