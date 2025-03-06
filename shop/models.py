from django.db import models
from django.utils import timezone
# Create your models here.


class Category(models.Model):
    title = models.CharField('Название', max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    title = models.CharField('Наименование', max_length=50)
    price = models.FloatField('Цена')
    volume = models.IntegerField('Масса')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(
        upload_to='products/', verbose_name="Изображение товара")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
