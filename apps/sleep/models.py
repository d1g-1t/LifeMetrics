from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimeStampedModel
from apps.users.models import User


class SleepLog(TimeStampedModel):
    
    QUALITY_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Fair'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_logs')
    
    date = models.DateField(db_index=True)
    bedtime = models.TimeField()
    wake_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0)])
    
    quality = models.IntegerField(choices=QUALITY_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'sleep_logs'
        ordering = ['-date']
        unique_together = [['user', 'date']]
        indexes = [
            models.Index(fields=['user', 'date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.duration_hours}h)"
