from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, db_index=True)
    telegram_username = models.CharField(max_length=255, blank=True)
    telegram_first_name = models.CharField(max_length=255, blank=True)
    telegram_last_name = models.CharField(max_length=255, blank=True)
    
    is_premium = models.BooleanField(default=False)
    premium_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.username or f"User {self.id}"


class UserProfile(TimeStampedModel):
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('light', 'Light (exercise 1-3 days/week)'),
        ('moderate', 'Moderate (exercise 3-5 days/week)'),
        ('active', 'Active (exercise 6-7 days/week)'),
        ('very_active', 'Very Active (intense exercise daily)'),
    ]
    
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('maintenance', 'Maintenance'),
        ('muscle_gain', 'Muscle Gain'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, default='sedentary')
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='maintenance')
    target_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    bmr = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    tdee = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    daily_calorie_target = models.IntegerField(null=True, blank=True)
    daily_protein_target = models.IntegerField(null=True, blank=True)
    daily_carbs_target = models.IntegerField(null=True, blank=True)
    daily_fat_target = models.IntegerField(null=True, blank=True)
    
    timezone = models.CharField(max_length=50, default='Europe/Moscow')
    language = models.CharField(max_length=10, default='ru')
    notifications_enabled = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_profiles'
        
    def __str__(self):
        return f"Profile: {self.user.username}"
    
    @property
    def age(self):
        if self.date_of_birth:
            from django.utils import timezone
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class TelegramSession(TimeStampedModel):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='telegram_sessions')
    telegram_id = models.BigIntegerField(db_index=True)
    chat_id = models.BigIntegerField()
    
    state = models.CharField(max_length=100, blank=True)
    state_data = models.JSONField(default=dict, blank=True)
    
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'telegram_sessions'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['telegram_id', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"Telegram Session: {self.user.username} - {self.telegram_id}"
