# Workout Tracker API

A REST API built with Flask, Flask-SQLAlchemy, Flask-Migrate, and Marshmallow. It manages workouts, reusable exercises, and the join records that store reps, sets, and duration.

## Install
Install Python 3.8.13+ and Pipenv. From the project root:
```bash
pip install pipenv
pipenv install --dev
cd server
pipenv run flask --app app db init
pipenv run flask --app app db migrate -m "create workout tables"
pipenv run flask --app app db upgrade
pipenv run python seed.py
```
If `server/migrations` already exists, skip `db init`.

## Run
From `server/`:
```bash
pipenv run flask --app app run --port 5555 --debug
```
API base URL: `http://127.0.0.1:5555`

## Endpoints
- `GET /workouts` — list workouts and their join records.
- `GET /workouts/<id>` — show one workout and its exercises.
- `POST /workouts` — create a workout.
- `DELETE /workouts/<id>` — delete a workout and its join records.
- `GET /exercises` — list exercises and associated workouts.
- `GET /exercises/<id>` — show one exercise and its workouts.
- `POST /exercises` — create an exercise.
- `DELETE /exercises/<id>` — delete an exercise and its join records.
- `POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` — attach an exercise with reps/sets/duration.

## Example requests
Create workout:
```bash
curl -X POST http://127.0.0.1:5555/workouts -H "Content-Type: application/json" -d '{"date":"2026-10-17","duration_minutes":45,"notes":"Strength day"}'
```
Create exercise:
```bash
curl -X POST http://127.0.0.1:5555/exercises -H "Content-Type: application/json" -d '{"name":"Push-ups","category":"Strength","equipment_needed":false}'
```
Attach exercise (IDs must exist):
```bash
curl -X POST http://127.0.0.1:5555/workouts/1/exercises/1/workout_exercises -H "Content-Type: application/json" -d '{"reps":12,"sets":3}'
```

## Validations
Database constraints enforce positive workout duration, non-blank exercise names, unique exercise names within a category, unique workout/exercise pairs, and positive optional reps/sets/duration. Model validators and Marshmallow schema validators also reject invalid input.

## Seed data
`pipenv run python seed.py` resets the current rows and inserts example workouts, exercises, and join records. It is safe to rerun.
