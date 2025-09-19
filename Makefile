# Django project settings
PROJECT_NAME = myproject
PROJECT_DIR = $(shell cd)
VENV_DIR = venv

# Python and pip versions
PYTHON = $(VENV_DIR)\Scripts\python.exe
PIP = $(VENV_DIR)\Scripts\pip.exe

# Django management commands
DJANGO_MANAGE = $(PYTHON) manage.py

# Make targets
all: help

help:
	@echo "Makefile for $(PROJECT_NAME)"
	@echo "---------------------------"
	@echo "Targets:"
	@echo "  make install      : Install dependencies"
	@echo "  make migrate      : Run database migrations"
	@echo "  make runserver    : Start development server"
	@echo "  make test         : Run tests"
	@echo "  make lint         : Run linting checks"
	@echo "  make clean        : Remove temporary files"
	@echo "  make venv         : Create virtual environment"

install:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt

freeze:
	@echo "Freeze dependencies..."
	$(PIP) freeze > requirements.txt

migrate:
	@echo "Running database migrations..."
	$(DJANGO_MANAGE) migrate

migrations:
	@echo "Running database make migrations..."
	$(DJANGO_MANAGE) makemigrations

su:
	@echo "Running createsuperuser..."
	$(DJANGO_MANAGE) createsuperuser

run:
	@echo "Starting development server..."
	$(DJANGO_MANAGE) runserver [::]:8001

test:
	@echo "Running tests..."
	$(DJANGO_MANAGE) test

lint:
	@echo "Running linting checks..."
	flake8 .

clean:
	@echo "Cleaning up temporary files..."
	PowerShell -Command "Get-ChildItem -Recurse -Include *.pyc, __pycache__ | Remove-Item -Recurse -Force"

venv:
	@echo "Creating virtual environment..."
	python -m venv $(VENV_DIR)
	@echo "Upgrading pip in the virtual environment..."
	$(PIP) install --upgrade pip

generate:
	python manage.py dumpdata $(model) --indent 2 > $(file_path)
