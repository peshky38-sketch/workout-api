from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from models import db, Workout, Exercise, WorkoutExercise
from schemas import WorkoutSchema, ExerciseSchema, WorkoutExerciseSchema

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
link_schema = WorkoutExerciseSchema()


def error(message, status):
    return jsonify({"error": message}), status


def json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError({"_schema": ["Body must be a JSON object."]})
    return data


@app.get("/")
def index():
    return jsonify({"message": "Workout Tracker API", "workouts": "/workouts", "exercises": "/exercises"})


@app.get("/workouts")
def list_workouts():
    return jsonify(workouts_schema.dump(Workout.query.order_by(Workout.id).all())), 200


@app.get("/workouts/<int:workout_id>")
def show_workout(workout_id):
    item = db.session.get(Workout, workout_id)
    if item is None:
        return error("Workout not found.", 404)
    return jsonify(workout_schema.dump(item)), 200


@app.post("/workouts")
def create_workout():
    try:
        data = workout_schema.load(json_object())
        item = Workout(**data)
        db.session.add(item)
        db.session.commit()
        return jsonify(workout_schema.dump(item)), 201
    except ValidationError as exc:
        db.session.rollback()
        return jsonify({"errors": exc.messages}), 400
    except ValueError as exc:
        db.session.rollback()
        return error(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error("Workout violates a database constraint.", 400)


@app.delete("/workouts/<int:workout_id>")
def remove_workout(workout_id):
    item = db.session.get(Workout, workout_id)
    if item is None:
        return error("Workout not found.", 404)
    db.session.delete(item)
    db.session.commit()
    return "", 204


@app.get("/exercises")
def list_exercises():
    return jsonify(exercises_schema.dump(Exercise.query.order_by(Exercise.id).all())), 200


@app.get("/exercises/<int:exercise_id>")
def show_exercise(exercise_id):
    item = db.session.get(Exercise, exercise_id)
    if item is None:
        return error("Exercise not found.", 404)
    return jsonify(exercise_schema.dump(item)), 200


@app.post("/exercises")
def create_exercise():
    try:
        data = exercise_schema.load(json_object())
        item = Exercise(**data)
        db.session.add(item)
        db.session.commit()
        return jsonify(exercise_schema.dump(item)), 201
    except ValidationError as exc:
        db.session.rollback()
        return jsonify({"errors": exc.messages}), 400
    except ValueError as exc:
        db.session.rollback()
        return error(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error("Duplicate exercise name/category or another database constraint failed.", 400)


@app.delete("/exercises/<int:exercise_id>")
def remove_exercise(exercise_id):
    item = db.session.get(Exercise, exercise_id)
    if item is None:
        return error("Exercise not found.", 404)
    db.session.delete(item)
    db.session.commit()
    return "", 204


@app.post("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def attach_exercise(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)
    if workout is None:
        return error("Workout not found.", 404)
    if exercise is None:
        return error("Exercise not found.", 404)
    try:
        data = link_schema.load(json_object())
        link = WorkoutExercise(workout_id=workout_id, exercise_id=exercise_id, **data)
        db.session.add(link)
        db.session.commit()
        return jsonify(link_schema.dump(link)), 201
    except ValidationError as exc:
        db.session.rollback()
        return jsonify({"errors": exc.messages}), 400
    except ValueError as exc:
        db.session.rollback()
        return error(str(exc), 400)
    except IntegrityError:
        db.session.rollback()
        return error("Exercise already attached to workout or data violates a constraint.", 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
