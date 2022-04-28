from django.db import models
from django.urls import reverse


class Weather(models.Model):
    WEATHER_TYPE = (
        ('Снег', 'Снег'),
        ('Дождь', 'Дождь'),
        ('Солнце', 'Солнце'),
        ('Облачность', 'Облачность'),
    )

    # create list with hours [(1, '1:00'), (2, '2:00'), ...]
    HOURS = [(h, f'{h}:00') for h in range(1, 25)]

    date = models.DateField(verbose_name='Дата')
    time = models.IntegerField(choices=HOURS, verbose_name='Время')
    city = models.CharField(max_length=100, verbose_name='Город')
    temperature = models.FloatField(verbose_name='Температура')
    weather = models.CharField(max_length=100, choices=WEATHER_TYPE, verbose_name='Характер погоды')

    class Meta:
        verbose_name = 'Данные о погоде'
        verbose_name_plural = 'Данные о погоде'
        ordering = ['-date', '-time']

    def __str__(self):
        return f'{self.date}, {self.time} {self.city} {self.temperature} {self.weather}'

    def get_absolute_url(self):
        return reverse('weather_detail', kwargs={'pk': self.pk})
