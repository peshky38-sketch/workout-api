from marshmallow import Schema, ValidationError, fields, validate, validates_schema


def nonblank(value):
    if not value.strip():
        raise ValidationError("Must not be blank.")


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, load_default=None, validate=validate.Range(min=1))
    sets = fields.Int(allow_none=True, load_default=None, validate=validate.Range(min=1))
    duration_seconds = fields.Int(allow_none=True, load_default=None, validate=validate.Range(min=1))
    exercise = fields.Nested(lambda: ExerciseSchema(only=("id", "name", "category", "equipment_needed")), dump_only=True)

    @validates_schema
    def require_measurement(self, data, **kwargs):
        if not any(data.get(k) is not None for k in ("reps", "sets", "duration_seconds")):
            raise ValidationError("Provide at least one of reps, sets, or duration_seconds.")


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.Str(allow_none=True, load_default=None, validate=validate.Length(max=2000))
    workout_exercises = fields.List(fields.Nested(WorkoutExerciseSchema), dump_only=True)


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=[validate.Length(min=1, max=100), nonblank])
    category = fields.Str(required=True, validate=[validate.Length(min=1, max=80), nonblank])
    equipment_needed = fields.Bool(required=True)
    workout_exercises = fields.List(
        fields.Nested(WorkoutExerciseSchema(only=("id", "workout_id", "reps", "sets", "duration_seconds"))),
        dump_only=True
    )
