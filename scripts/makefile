default:
	@cat makefile

ENV = env
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip


env:
	python3 -m venv $(ENV); $(PIP) install --upgrade pip

update:  env
	$(PIP) install -r requirements.txt

lint: update
	$(PYTHON) -m pylint bin/ tests/

test: lint
	$(PYTHON) -m pytest tests/

run: update
	$(PYTHON) -u bin/enrich_transcripts.py < mock_transcripts.jsonl | $(PYTHON) bin/validate_schema.py

.PHONY: load
load:
	@echo "Initiating Cloud Data Warehouse Synchronizer Node..."
	cat mock_transcripts.jsonl | python bin/load_snowflake.py

REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

docker_build:
	docker build -t sdhersee/ds5111-pipeline:latest -f $(REPO_ROOT)/Dockerfile $(REPO_ROOT)

docker_run:
	cat $(REPO_ROOT)/scripts/youtube_ids | docker run -i \
	 -v "$(REPO_ROOT)/scripts/logs:/app/logs" \
	 --env-file $(REPO_ROOT)/scripts/bin/.env \
	 sdhersee/ds5111-pipeline:latest

docker_rebuild-run: docker_build docker_run

.PHONY: default env update lint test run load docker_build docker_run docker_rebuild-run
