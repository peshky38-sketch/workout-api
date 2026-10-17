from datetime import date
from app import app
from models import db, Workout, Exercise, WorkoutExercise

with app.app_context():
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    pushups = Exercise(name="Push-ups", category="Strength", equipment_needed=False)
    squats = Exercise(name="Squats", category="Strength", equipment_needed=False)
    cycling = Exercise(name="Cycling", category="Cardio", equipment_needed=True)
    workout1 = Workout(date=date(2026, 10, 17), duration_minutes=45, notes="Strength session")
    workout2 = Workout(date=date(2026, 10, 18), duration_minutes=30, notes="Cardio session")
    db.session.add_all([pushups, squats, cycling, workout1, workout2])
    db.session.flush()
    db.session.add_all([
        WorkoutExercise(workout=workout1, exercise=pushups, reps=12, sets=3),
        WorkoutExercise(workout=workout1, exercise=squats, reps=10, sets=4),
        WorkoutExercise(workout=workout2, exercise=cycling, duration_seconds=1800),
    ])
    db.session.commit()
    print("Seed complete: 2 workouts, 3 exercises, 3 links.")
