SERVER := server
UV := uv --directory $(SERVER)

.PHONY: install run cli test

install:            ## create server/.venv and install deps (incl. dev)
	$(UV) sync

run:                ## start the server (host/port from settings)
	$(UV) run python -m pfa_server.main

cli:                ## interactive text client; override URL with: make cli URL=ws://host:8000/ws/session
	$(UV) run python tools/chat_cli.py $(if $(URL),--url $(URL))

test:               ## run pytest
	$(UV) run pytest -q
