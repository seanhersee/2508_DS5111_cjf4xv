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
