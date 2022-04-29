from django import forms
from django.forms import ValidationError

from web_app.models import Weather


class BaseCreateForm(forms.ModelForm):
    class Meta:
        model = Weather
        fields = ['date', 'time', 'city', 'temperature', 'weather']
        widgets = {
            'date': forms.SelectDateWidget(),
        }

    def clean(self):
        for error in self.errors:
            if error:
                return

        weather_type = self.cleaned_data.get('weather', None)
        temperature = int(self.cleaned_data.get('temperature', None))

        if not self._is_weather_type_correct(weather_type, temperature):
            raise ValidationError('Температура и тип погоды не соответствуют друг другу')

    @staticmethod
    def _is_weather_type_correct(weather_type: str, temperature: int) -> bool:
        if temperature > 0 and weather_type == 'Снег' or temperature < 0 and weather_type == 'Дождь':
            return False
        return True


class WeatherUpdateForm(BaseCreateForm):
    pass


class WeatherCreateForm(BaseCreateForm):
    def clean(self):
        super().clean()

        date = self.cleaned_data.get('date', None)
        time = self.cleaned_data.get('time', None)
        city = self.cleaned_data.get('city', None)

        if self._is_weather_data_exist_in_db(date=date, time=time, city=city):
            raise ValidationError(f'Для {city} данные на {date} время {time}:00 уже занесены')

    @staticmethod
    def _is_weather_data_exist_in_db(date: str, time: str, city: str) -> bool:
        return Weather.objects.filter(date=date, time=time, city=city).exists()
