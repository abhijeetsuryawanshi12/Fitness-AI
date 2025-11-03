# Pydantic Validation Fix for Plan Generation

## Common Pydantic Validation Issues

The plan generation is failing Pydantic validation because the LLM (Gemini) sometimes returns data that doesn't match the exact schema expected by your Pydantic models.

## Common Issues:

1. **Missing Required Fields** - LLM doesn't include all required fields
2. **Wrong Types** - LLM returns string instead of int/float, or vice versa
3. **Extra Fields** - LLM adds fields not in your schema
4. **Nested Structure Mismatch** - LLM nests data differently than expected

## Solution: Add Field Validators and Defaults

Here's the fix for `app/agents/plan_agent.py`:

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional

class NutritionFacts(BaseModel):
    calories: int = Field(default=0)
    protein: float = Field(default=0.0)
    carbs: float = Field(default=0.0)
    total_fat: float = Field(default=0.0)
    saturated_fat: float = Field(default=0.0)
    trans_fat: float = Field(default=0.0)
    polyunsaturated_fat: float = Field(default=0.0)
    monounsaturated_fat: float = Field(default=0.0)
    cholesterol: float = Field(default=0.0)
    sodium: float = Field(default=0.0)
    dietary_fiber: float = Field(default=0.0)
    sugar: float = Field(default=0.0)
    added_sugar: float = Field(default=0.0)
    sugar_alcohols: float = Field(default=0.0)
    vitamin_d: float = Field(default=0.0)
    calcium: float = Field(default=0.0)
    iron: float = Field(default=0.0)
    potassium: float = Field(default=0.0)
    vitamin_a: float = Field(default=0.0)
    vitamin_c: float = Field(default=0.0)

    @field_validator('*', mode='before')
    def coerce_to_number(cls, v):
        """Convert any value to appropriate number type"""
        if v is None or v == '':
            return 0
        try:
            return float(v) if '.' in str(v) else int(v)
        except (ValueError, TypeError):
            return 0

class TimeStruct(BaseModel):
    hour: int = Field(default=0, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    second: int = Field(default=0, ge=0, le=59)

    @field_validator('hour', 'minute', 'second', mode='before')
    def coerce_to_int(cls, v):
        """Convert to int, default to 0 if invalid"""
        if v is None or v == '':
            return 0
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0

class Meal(BaseModel):
    meal_name: str
    nutrition_facts: NutritionFacts
    task_time: TimeStruct

    @field_validator('meal_name', mode='before')
    def validate_meal_name(cls, v):
        """Ensure meal_name is not empty"""
        if not v or not str(v).strip():
            return "Unnamed Meal"
        return str(v).strip()

class Exercise(BaseModel):
    name: str
    sets: int = Field(default=3, gt=0)
    reps: int = Field(default=10, gt=0)
    weights: List[float] = Field(default_factory=list)
    instructions: str = Field(default="")
    task_time: TimeStruct

    @field_validator('name', mode='before')
    def validate_name(cls, v):
        """Ensure name is not empty"""
        if not v or not str(v).strip():
            return "Unnamed Exercise"
        return str(v).strip()

    @field_validator('sets', 'reps', mode='before')
    def coerce_to_int(cls, v):
        """Convert to int, default to safe value"""
        if v is None or v == '':
            return 3
        try:
            return max(1, int(v))
        except (ValueError, TypeError):
            return 3

    @field_validator('weights', mode='before')
    def validate_weights(cls, v):
        """Ensure weights is a list of floats"""
        if not v:
            return [0.0]
        if isinstance(v, (int, float)):
            return [float(v)]
        if isinstance(v, list):
            result = []
            for item in v:
                try:
                    result.append(float(item))
                except (ValueError, TypeError):
                    result.append(0.0)
            return result if result else [0.0]
        return [0.0]

class DailyPlan(BaseModel):
    day: int = Field(..., ge=1, le=7)
    theme: str
    exercises: List[Exercise] = Field(default_factory=list)
    meals: List[Meal] = Field(default_factory=list)

    @field_validator('day', mode='before')
    def validate_day(cls, v):
        """Ensure day is between 1-7"""
        try:
            day_int = int(v)
            return max(1, min(7, day_int))
        except (ValueError, TypeError):
            return 1

    @field_validator('theme', mode='before')
    def validate_theme(cls, v):
        """Ensure theme is not empty"""
        if not v or not str(v).strip():
            return "Workout Day"
        return str(v).strip()

class FullPlan(BaseModel):
    title: str
    daily_plan: List[DailyPlan]

    @field_validator('title', mode='before')
    def validate_title(cls, v):
        """Ensure title is not empty"""
        if not v or not str(v).strip():
            return "Fitness Plan"
        return str(v).strip()

    @model_validator(mode='after')
    def validate_daily_plan(self):
        """Ensure we have at least some days"""
        if not self.daily_plan:
            raise ValueError("Plan must have at least one day")
        return self
```

## Alternative: Make Fields Optional

If you want to be even more lenient:

```python
class NutritionFacts(BaseModel):
    calories: Optional[int] = 0
    protein: Optional[float] = 0.0
    carbs: Optional[float] = 0.0
    # ... etc
```

## Testing the Fix

After updating, test with:

```python
# Test data
test_plan = {
    "title": "Test Plan",
    "daily_plan": [
        {
            "day": 1,
            "theme": "Push Day",
            "exercises": [
                {
                    "name": "Bench Press",
                    "sets": "3",  # String instead of int
                    "reps": 10,
                    "weights": [50],
                    "instructions": "Lower bar to chest",
                    "task_time": {"hour": 9, "minute": 0, "second": 0}
                }
            ],
            "meals": []
        }
    ]
}

# Should not raise validation error
validated = FullPlan(**test_plan)
print(validated)
```

## Quick Fix Without Code Changes

If you can't modify the code right now, you can:

1. **Restart the backend** to clear any cached validation
2. **Check LLM output** - add more logging before validation
3. **Use the fallback** - The code already returns raw dict on validation failure (line 432)

## Logging for Debugging

Add this before validation (line 425):

```python
print("Final plan dict before validation:")
print(json.dumps(final_plan_dict, indent=2, default=str))
```

This will show you exactly what data is failing validation.
