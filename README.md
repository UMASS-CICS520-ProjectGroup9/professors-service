
# Professors Service

This Django RESTful service provides endpoints for managing professors and their reviews.

## Features
- List, retrieve, create, and delete professors
- Create and update reviews for professors

## API Endpoints

### Professors
- `GET /api/professors/` — List all professors (supports `?query=` for name/department search)
- `GET /api/professors/<id>/` — Retrieve a single professor
- `POST /api/professors/create/` — Create a professor (STAFF only)
- `DELETE /api/professors/<id>/delete/` — Delete a professor (STAFF only)

### Reviews
- `POST /api/professors/<id>/review/` — Create or update a review for a professor (STUDENT only)
    - If the user already reviewed, updates the review; otherwise, creates a new one.

## Data Models

### Professor
- `name` (CharField)
- `department` (CharField)
- `email` (EmailField)
- `office` (CharField)
- `rating` (FloatField)
- `creator_id` (IntegerField)

### Review
- `professor` (ForeignKey to Professor)
- `author` (CharField)
- `creator_id` (IntegerField)
- `rating` (IntegerField)
- `comment` (TextField)
- `created_at` (DateTimeField)

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
