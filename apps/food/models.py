from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimeStampedModel, SoftDeleteModel
from apps.users.models import User


class Food(TimeStampedModel, SoftDeleteModel):
    
    name = models.CharField(max_length=255, db_index=True)
    brand = models.CharField(max_length=255, blank=True)
    
    calories = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    protein = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    carbs = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    fat = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    fiber = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    sugar = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    
    serving_size = models.DecimalField(max_digits=7, decimal_places=2, default=100)
    barcode = models.CharField(max_length=50, blank=True, db_index=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='custom_foods')
    is_verified = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'foods'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'is_public']),
            models.Index(fields=['barcode']),
            models.Index(fields=['created_by', 'is_deleted']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.brand})" if self.brand else self.name


class FoodLog(TimeStampedModel):
    
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_logs')
    food = models.ForeignKey(Food, on_delete=models.PROTECT, related_name='logs')
    
    date = models.DateField(db_index=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    
    serving_amount = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    
    calories = models.DecimalField(max_digits=7, decimal_places=2)
    protein = models.DecimalField(max_digits=6, decimal_places=2)
    carbs = models.DecimalField(max_digits=6, decimal_places=2)
    fat = models.DecimalField(max_digits=6, decimal_places=2)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'food_logs'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'meal_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.food.name} ({self.date})"
    
    def save(self, *args, **kwargs):
        if not self.calories:
            multiplier = float(self.serving_amount) / 100  # Food nutrition is per 100g
            self.calories = float(self.food.calories) * multiplier
            self.protein = float(self.food.protein) * multiplier
            self.carbs = float(self.food.carbs) * multiplier
            self.fat = float(self.food.fat) * multiplier
        super().save(*args, **kwargs)


class DailySummary(TimeStampedModel):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_summaries')
    date = models.DateField(db_index=True)
    
    total_calories = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    total_protein = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_carbs = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_fat = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    target_calories = models.IntegerField(null=True, blank=True)
    target_protein = models.IntegerField(null=True, blank=True)
    target_carbs = models.IntegerField(null=True, blank=True)
    target_fat = models.IntegerField(null=True, blank=True)
    
    breakfast_calories = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    lunch_calories = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    dinner_calories = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    snack_calories = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    
    water_intake_ml = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'daily_summaries'
        ordering = ['-date']
        unique_together = [['user', 'date']]
        indexes = [
            models.Index(fields=['user', 'date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    @property
    def calorie_percentage(self):
        if self.target_calories:
            return (float(self.total_calories) / self.target_calories) * 100
        return 0


class WaterLog(TimeStampedModel):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_logs')
    date = models.DateField(db_index=True)
    amount_ml = models.IntegerField(validators=[MinValueValidator(0)])
    time = models.TimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'water_logs'
        ordering = ['-date', '-time']
        indexes = [
            models.Index(fields=['user', 'date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.amount_ml}ml ({self.date})"
