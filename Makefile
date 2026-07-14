.PHONY: api web test docker seed

api:
	cd apps/api && uvicorn app.main:app --reload

web:
	cd apps/web && npm run dev

test:
	cd apps/api && pytest -q

docker:
	docker compose up --build
