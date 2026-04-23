# CivicMind — Makefile for common tasks
# Usage: make <target>

.PHONY: help install test train eval api dashboard docker-build docker-run clean

help:
	@echo "CivicMind — Available Commands:"
	@echo "  make install       Install dependencies"
	@echo "  make test          Run tests"
	@echo "  make train         Train model locally"
	@echo "  make eval          Run evaluation"
	@echo "  make api           Start API server"
	@echo "  make dashboard     Start Streamlit dashboard"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-run    Run full stack with Docker Compose"
	@echo "  make clean         Remove generated files"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	python -m pytest tests/ -v

train:
	python training/data_generator.py --n_samples 500
	python training/train_grpo.py --mode train --epochs 2 --max_weeks 12

eval:
	python evaluate.py --mode compare --n_episodes 3 --difficulty 3

api:
	uvicorn apis.mock_apis:app --host 0.0.0.0 --port 8080 --reload

dashboard:
	streamlit run demo/dashboard.py

docker-build:
	docker build -t civicmind:latest .

docker-run:
	docker-compose up -d api dashboard

docker-train:
	docker-compose --profile training run trainer

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf build/ dist/ *.egg-info/
	rm -rf training/checkpoints/*
	rm -rf evaluation/*.png evaluation/*.json
	rm -rf logs/*.log
