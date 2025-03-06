from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bonus_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.bonus_points} points"

    def add_bonus_points(self, points):
        """Метод для начисления бонусов"""
        self.bonus_points += points
        self.save()

    def deduct_bonus_points(self, points):
        """Метод для списания бонусов"""
        if self.bonus_points >= points:
            self.bonus_points -= points
            self.save()
            return True
        else:
            return False  # Недостаточно бонусов для списания


class BonusTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} points - {self.description}"
