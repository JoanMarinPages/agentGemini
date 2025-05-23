# Makefile para agentGemini

.PHONY: help setup install run test clean format lint

# Colores
COLOR_RESET = \033[0m
COLOR_BOLD = \033[1m
COLOR_GREEN = \033[32m
COLOR_YELLOW = \033[33m

help: ## Muestra esta ayuda
	@echo "$(COLOR_BOLD)Comandos disponibles:$(COLOR_RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_GREEN)%-15s$(COLOR_RESET) %s\n", $$1, $$2}'

setup: ## Configura el entorno de desarrollo
	@echo "$(COLOR_YELLOW)Configurando entorno...$(COLOR_RESET)"
	@bash scripts/setup.sh

install: ## Instala las dependencias
	@echo "$(COLOR_YELLOW)Instalando dependencias...$(COLOR_RESET)"
	@pip install -r requirements.txt

run: ## Ejecuta el agente en modo desarrollo
	@echo "$(COLOR_YELLOW)Ejecutando agente...$(COLOR_RESET)"
	@bash scripts/run_dev.sh

run-web: ## Ejecuta el agente con interfaz web
	@echo "$(COLOR_YELLOW)Ejecutando agente con interfaz web...$(COLOR_RESET)"
	@adk web agent.py

test: ## Ejecuta los tests
	@echo "$(COLOR_YELLOW)Ejecutando tests...$(COLOR_RESET)"
	@bash scripts/test.sh

format: ## Formatea el código
	@echo "$(COLOR_YELLOW)Formateando código...$(COLOR_RESET)"
	@black .
	@isort .

lint: ## Ejecuta los linters
	@echo "$(COLOR_YELLOW)Ejecutando linters...$(COLOR_RESET)"
	@flake8 .
	@mypy .

clean: ## Limpia archivos temporales
	@echo "$(COLOR_YELLOW)Limpiando archivos temporales...$(COLOR_RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(COLOR_GREEN)Limpieza completada$(COLOR_RESET)"

build: clean ## Construye el proyecto
	@echo "$(COLOR_YELLOW)Construyendo proyecto...$(COLOR_RESET)"
	@python -m build

docs: ## Genera la documentación
	@echo "$(COLOR_YELLOW)Generando documentación...$(COLOR_RESET)"
	@cd docs && make html
