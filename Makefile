.DEFAULT_GOAL := help
SHELL := /bin/bash
VENV := .venv-test

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

$(VENV):
	@echo "Creando entorno de test en $(VENV)/ (sólo la primera vez)..."
	@python3 -m venv $(VENV)
	@$(VENV)/bin/pip install -q --upgrade pip
	@$(VENV)/bin/pip install -q -r osb/requirements.txt -r osb/requirements-test.txt

test: $(VENV)  ## Correr los tests del OSB (rápido, NO necesita docker)
	@cd osb && ../$(VENV)/bin/python -m pytest tests/ -q

security: $(VENV)  ## Escaneo de seguridad: linter bandit + secretos en el historial
	@echo "── Linter de seguridad (reglas bandit) ───────────────────"
	@$(VENV)/bin/ruff check --no-cache . && echo "Sin hallazgos."
	@echo ""
	@echo "── Secretos en el árbol de trabajo ───────────────────────"
	@git ls-files -z | xargs -0 grep -lE '(sk-ant-[A-Za-z0-9_-]{20}|ghp_[A-Za-z0-9]{30}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)' 2>/dev/null \
		&& echo "  ↑ ARCHIVOS CON POSIBLES CREDENCIALES — revisalos" \
		|| echo "Sin credenciales con formato reconocible."
	@echo ""
	@echo "── ¿Está .env versionado por error? ──────────────────────"
	@git ls-files --error-unmatch .env >/dev/null 2>&1 \
		&& echo "  PELIGRO: .env está en git. Sacalo YA y rotá todos los secretos." \
		|| echo "OK, .env no está versionado."
	@echo ""
	@echo "── Dependencias con vulnerabilidades conocidas ───────────"
	@$(VENV)/bin/pip install -q pip-audit 2>/dev/null; \
	 $(VENV)/bin/pip-audit -r osb/requirements.txt --progress-spinner off 2>&1 | tail -20 \
		|| echo "(pip-audit no disponible, se salteó este chequeo)"

test-deps:  ## Rehacer el entorno de test desde cero
	@rm -rf $(VENV)
	@$(MAKE) --no-print-directory test

health:  ## Chequear que los servicios responden
	@echo "OSB        → $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health || echo 'sin respuesta')"
	@echo "Sovereign  → $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8081/ || echo 'sin respuesta')"
	@echo "Envoy      → $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:9901/ready || echo 'sin respuesta')"
	@echo "Prometheus → $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/-/healthy || echo 'sin respuesta')"
	@echo "Grafana    → $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3002/api/health || echo 'sin respuesta')"
	@echo "(200 o 204 = OK. 000 o 'sin respuesta' = ese servicio no está levantado)"

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
