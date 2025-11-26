from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import TimeStampedModel
from apps.users.models import User


class Goal(TimeStampedModel):
    
    GOAL_TYPE_CHOICES = [
        ('weight', 'Weight Goal'),
        ('calories', 'Daily Calories'),
        ('workout_frequency', 'Workout Frequency'),
        ('water', 'Daily Water'),
        ('sleep', 'Sleep Duration'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    start_date = models.DateField()
    target_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    class Meta:
        db_table = 'goals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'goal_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    @property
    def progress_percentage(self):
        if self.target_value > 0:
            return min((float(self.current_value) / float(self.target_value)) * 100, 100)
        return 0


class Achievement(TimeStampedModel):
    
    CATEGORY_CHOICES = [
        ('streak', 'Streak'),
        ('milestone', 'Milestone'),
        ('consistency', 'Consistency'),
        ('challenge', 'Challenge'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    icon = models.CharField(max_length=100, blank=True)
    points = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'achievements'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserAchievement(TimeStampedModel):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_achievements'
        unique_together = [['user', 'achievement']]
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"
