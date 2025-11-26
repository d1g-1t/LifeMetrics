from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import TimeStampedModel
from apps.users.models import User


class Workout(TimeStampedModel):
    
    CATEGORY_CHOICES = [
        ('cardio', 'Cardio'),
        ('strength', 'Strength Training'),
        ('flexibility', 'Flexibility'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    calories_per_hour = models.IntegerField(validators=[MinValueValidator(0)])
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'workouts'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class WorkoutLog(TimeStampedModel):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_logs')
    workout = models.ForeignKey(Workout, on_delete=models.PROTECT, related_name='logs')
    
    date = models.DateField(db_index=True)
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)])
    calories_burned = models.IntegerField(validators=[MinValueValidator(0)])
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'workout_logs'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.workout.name} ({self.date})"
