# Professors Service

This Django service provides a RESTful API for retrieving professor data.

## Features
- List all professors

## API Endpoints
- `GET /api/professors/` — List all professors

## Data Model
The `Professor` model includes:
- `name` (CharField)
- `department` (CharField)
- `email` (EmailField)
- `office` (CharField)
- `rating` (FloatField)

## Requirements
Add these to `requirements.txt`:

```
Django>=5.2
djangorestframework>=3.14
```

## Setup & Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. Run server:
   ```bash
   python manage.py runserver 9003
   ```
