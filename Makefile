.DEFAULT_GOAL := help
SHELL := /bin/bash

help:  ## Mostrar esta ayuda
	@awk 'BEGIN {FS = ":.*##"; printf "Comandos disponibles:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

up:  ## Levantar toda la plataforma
	docker-compose up -d --build

down:  ## Apagar todo
	docker-compose down

restart:  ## Reiniciar todo
	docker-compose restart

logs:  ## Ver logs en vivo
	docker-compose logs -f --tail=100

ps:  ## Ver estado de los servicios
	docker-compose ps

clean:  ## Apagar y borrar volúmenes (CUIDADO: borra datos)
	docker-compose down -v

demo:  ## Cargar datos de demo (servicios echo y orders)
	@echo "Creando servicio echo-demo..."
	@curl -sS -X POST http://localhost:8000/v1/services \
		-H 'Content-Type: application/json' \
		-d '{"name":"echo-demo","team":"platform","upstream_host":"echo-service","upstream_port":8080,"public_path":"/echo","requires_auth":false,"rate_limit_rpm":1000}'
	@echo ""
	@echo "Creando servicio orders-api..."
	@curl -sS -X POST http://localhost:8000/v1/services \
		-H 'Content-Type: application/json' \
		-d '{"name":"orders-api","team":"payments","upstream_host":"orders-service","upstream_port":8080,"public_path":"/orders","requires_auth":true,"rate_limit_rpm":300}'
	@echo ""
	@echo "OK. Esperá 3 segundos a que el worker procese y luego: curl http://localhost:10000/echo"

token:  ## Generar un JWT de prueba
	@docker-compose exec auth-sidecar python -c "import jwt, time; print(jwt.encode({'sub':'naim','iat':int(time.time()),'exp':int(time.time())+3600}, 'dev-only-secret-change-me-min-32-chars!!', algorithm='HS256'))"

test-edge:  ## Probar tráfico contra Envoy (no requiere auth)
	curl -sS http://localhost:10000/echo/hello | jq .

test-edge-auth:  ## Probar endpoint que requiere auth (usa make token)
	@TOKEN=$$(make token | tail -1); curl -sS -H "Authorization: Bearer $$TOKEN" http://localhost:10000/orders | jq .

dashboard:  ## Abrir el dashboard del OSB
	@echo "OSB UI:        http://localhost:8000"
	@echo "API docs:      http://localhost:8000/docs"
	@echo "Envoy admin:   http://localhost:9901"
	@echo "Sovereign:     http://localhost:8081"
	@echo "Prometheus:    http://localhost:9090"
	@echo "Grafana:       http://localhost:3002 (anon viewer)"
