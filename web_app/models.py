from django.db import models
from django.urls import reverse


class Weather(models.Model):
    WEATHER_TYPE = (
        ('Снег', 'Снег'),
        ('Дождь', 'Дождь'),
        ('Солнце', 'Солнце'),
        ('Облачность', 'Облачность'),
    )

    HOURS = (
        (1, '1:00'), (2, '2:00'), (3, '3:00'), (4, '4:00'), (5, '5:00'), (6, '6:00'),
        (7, '7:00'), (8, '8:00'), (9, '9:00'), (10, '10:00'), (11, '11:00'), (12, '12:00'),
        (13, '13:00'), (14, '14:00'), (15, '15:00'), (16, '16:00'), (17, '17:00'), (18, '18:00'),
        (19, '19:00'), (20, '20:00'), (21, '21:00'), (22, '22:00'), (23, '23:00'), (24, '24:00')
    )

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
