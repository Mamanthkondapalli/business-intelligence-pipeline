.PHONY: setup generate etl dashboard all

setup:
	pip install -r requirements.txt

generate:
	python src/generate_data.py

etl:
	python src/etl.py

dashboard:
	python src/dashboard.py

all: generate etl
	@echo "Pipeline complete. Run 'make dashboard' to open http://localhost:8050"
