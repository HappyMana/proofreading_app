# Makefile for Japanese Proofreading System

.PHONY: help install dev build test lint format clean docker-up docker-down docker-build

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Start development environment"
	@echo "  build       - Build production"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linters"
	@echo "  format      - Format code"
	@echo "  clean       - Clean temporary files"
	@echo "  docker-up   - Start Docker services"
	@echo "  docker-down - Stop Docker services"
	@echo "  docker-build- Build Docker images"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Start development environment
dev:
	@echo "Starting development environment..."
	docker-compose up -d

# Build production
build:
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "Building backend..."
	cd backend && python -m build

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && python -m pytest
	@echo "Running frontend tests..."
	cd frontend && npm test

# Run linters
lint:
	@echo "Running backend linters..."
	cd backend && flake8 app/ tests/
	cd backend && mypy app/
	@echo "Running frontend linters..."
	cd frontend && npm run lint

# Format code
format:
	@echo "Formatting backend code..."
	cd backend && black app/ tests/
	cd backend && isort app/ tests/
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf backend/dist/
	rm -rf frontend/.next/
	rm -rf frontend/out/

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

# Development shortcuts
backend-dev:
	cd backend && uvicorn app.main:app --reload

frontend-dev:
	cd frontend && npm run dev