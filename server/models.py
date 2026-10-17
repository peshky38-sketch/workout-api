from datetime import date as date_type
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Workout(db.Model):
    __tablename__ = "workouts"
    __table_args__ = (CheckConstraint("duration_minutes > 0", name="ck_workout_duration_positive"),)
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date_type.today)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    workout_exercises = db.relationship("WorkoutExercise", back_populates="workout",
                                        cascade="all, delete-orphan")
    exercises = db.relationship("Exercise", secondary="workout_exercises",
                                viewonly=True, back_populates="workouts")

    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("duration_minutes must be a positive integer")
        return value


class Exercise(db.Model):
    __tablename__ = "exercises"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_exercise_name_nonblank"),
        UniqueConstraint("name", "category", name="uq_exercise_name_category"),
    )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship("WorkoutExercise", back_populates="exercise",
                                        cascade="all, delete-orphan")
    workouts = db.relationship("Workout", secondary="workout_exercises",
                               viewonly=True, back_populates="exercises")

    @validates("name", "category")
    def validate_text(self, key, value):
        max_len = 100 if key == "name" else 80
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string")
        if len(value.strip()) > max_len:
            raise ValueError(f"{key} must be at most {max_len} characters")
        return value.strip()

    @validates("equipment_needed")
    def validate_equipment(self, key, value):
        if not isinstance(value, bool):
            raise ValueError("equipment_needed must be true or false")
        return value


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise_pair"),
        CheckConstraint("reps IS NULL OR reps > 0", name="ck_reps_positive"),
        CheckConstraint("sets IS NULL OR sets > 0", name="ck_sets_positive"),
        CheckConstraint("duration_seconds IS NULL OR duration_seconds > 0", name="ck_seconds_positive"),
    )
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("reps", "sets", "duration_seconds")
    def validate_counts(self, key, value):
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value <= 0):
            raise ValueError(f"{key} must be a positive integer or null")
        return value
