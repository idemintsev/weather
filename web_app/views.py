import json
import urllib.parse as urlparse
from collections import namedtuple, defaultdict
from typing import Tuple, List
from urllib.parse import parse_qs

from django.core.serializers import serialize
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from weather.settings import HOSTNAME
from web_app.forms import WeatherCreateForm, WeatherUpdateForm
from web_app.models import Weather

MAIN_MENU = (
    {'title': 'Просмотреть данные', 'url_name': 'weather_list'},
    {'title': 'Добавить данные', 'url_name': 'weather_create'},
    {'title': 'Редактировать данные', 'url_name': 'editor'},
    {'title': 'Дашборд', 'url_name': 'dashboard'},
    {'title': 'Импортировать данные', 'url_name': 'import_data_info'},
)


class MainPageView(View):
    def get(self, request):
        return render(request, 'web_app/base.html', {'menu': MAIN_MENU})


class BaseWeather:
    model = Weather


class WeatherListView(BaseWeather, ListView):
    template_name = 'web_app/weather_list.html'
    context_object_name = 'weather_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._update_context(context)
        context['menu'] = MAIN_MENU
        return context

    def _update_context(self, context):
        date, time, city, temperature, weather = self._get_values_from_queryset_for_filter(context)
        context.update(date=date, time=time, city=city, temperature=temperature, weather=weather)

    @staticmethod
    def _get_values_from_queryset_for_filter(context) -> Tuple:
        '''
        Get unique values for filter checkboxes in template filter.html.
        '''
        date, time, city, temperature, weather = set(), set(), set(), set(), set()
        for el in context.get('object_list', ()):
            date.add(el.date)
            time.add(el.time)
            city.add(el.city)
            temperature.add(el.temperature)
            weather.add(el.weather)
        city.add('All cities')
        return sorted(list(date)), sorted(list(time)), sorted(list(city)), sorted(list(temperature)), \
               sorted(list(weather))

    def _get_filter_values_from_request(self) -> dict:
        filter_params = {key: value for key, value in self.request.GET.items() if bool(len(value))}
        if 'datefilter' in filter_params:
            datefilter = filter_params.pop('datefilter', '').replace(' ', '')
            date = datefilter.split('/')
            filter_params.update(date__range=date)
        filter_params.pop('sorted_by', None)
        return filter_params

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get('sorted_by', None):
            filter_params = self._get_filter_values_from_request()
            if 'All cities' in filter_params.values():
                # remove because we will not need this value for getting queryset
                filter_params.pop('city')
            queryset = Weather.objects.filter(
                **filter_params,
            )
            return queryset
        return queryset


class WeatherCreateView(BaseWeather, CreateView):
    form_class = WeatherCreateForm
    template_name = 'web_app/weather_create.html'
    success_url = '/weather/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = MAIN_MENU
        return context


class WeatherEditorView(WeatherListView):
    template_name = 'web_app/editor.html'


class WeatherDetailView(BaseWeather, DetailView):
    template_name = 'web_app/weather_detail.html'


class WeatherUpdateView(BaseWeather, UpdateView):
    template_name = 'web_app/weather_update.html'
    form_class = WeatherUpdateForm


class WeatherDeleteView(BaseWeather, DeleteView):
    template_name = 'web_app/weather_delete.html'
    success_url = '/editor/'


class DashboardView(View):
    def get(self, request, *args, **kwargs):
        date_for_filter, temperature_for_filter, city_for_filter = self._get_values_from_queryset_for_filter()
        context = {
            'menu': MAIN_MENU, 'date': date_for_filter, 'city': city_for_filter, 'temperature': temperature_for_filter
        }

        if request.GET.get('sorted_by', None):
            filter_params = {key: value for key, value in self.request.GET.items() if bool(len(value))}
            if 'datefilter' in filter_params:
                datefilter = filter_params.pop('datefilter', '').replace(' ', '')
                date = datefilter.split('/')
                filter_params.update(date__range=date)

            filter_params.pop('sorted_by')

            weather = Weather.objects.filter(**filter_params)
            weather_dates = []
            weather_temperatures = []
            city = ''

            for _data in weather:
                weather_dates.append(f'{_data.date} {_data.time}:00')
                weather_temperatures.append(f'{int(_data.temperature)}')
                city = _data.city

            data = json.dumps({
                            'title': 'График погоды',
                            'subtitle': f'Для города {city}',
                            'date': weather_dates,
                            'city': city,
                            'temperature': weather_temperatures
                        })
            context['data'] = data

        return render(request, 'web_app/dashboard.html', context)

    def _update_context(self, context):
        date, time, city, temperature, weather = self._get_values_from_queryset_for_filter(context)
        context.update(date=date, time=time, city=city, temperature=temperature, weather=weather)

    def _get_values_from_queryset_for_filter(self) -> Tuple:
        '''
        Get unique values for filter checkboxes in template filter.html.
        '''
        date, time, city, = set(), set(), set()
        qset = Weather.objects.all()
        for el in qset:
            date.add(el.date)
            time.add(el.time)
            city.add(el.city)
        return sorted(list(date)), sorted(list(time)), sorted(list(city))


@method_decorator(csrf_exempt, name='dispatch')
class WeatherJsonView(View):
    def get(self, request, *args, **kwargs):

        filter_parameters = self._get_filter_params_from_url()
        if filter_parameters:
            if 'All cities' in filter_parameters.get('city__in', []):
                filter_parameters.pop('city__in')
            if 'sorted_by__in' in filter_parameters:
                filter_parameters.pop('sorted_by__in')

            weather = Weather.objects.filter(**filter_parameters)
        else:
            weather = Weather.objects.all()

        weather_serialized_data = serialize('python', weather)
        data = {
            'weather': weather_serialized_data,
        }
        return JsonResponse(data)

    def post(self, request):
        post_body = json.loads(request.body)

        is_data_valid = self._is_data_from_json_correct(post_body)

        if not is_data_valid.status:
            return JsonResponse(is_data_valid.message, status=422)

        objs = [
            Weather(
                date=_data['date'],
                time=_data['time'],
                city=_data['city'],
                temperature=_data['temperature'],
                weather=_data['weather'],
            )
            for _data in post_body
        ]

        weather_objs = Weather.objects.bulk_create(objs)
        data = {
            'message': f'Weather data has been created {weather_objs}'
        }
        return JsonResponse(data, status=201)

    def _is_data_from_json_correct(self, json_data: List[dict]) -> namedtuple:
        JSONCheckResult = namedtuple('JSONCheckResult', 'status message')
        filter_data = defaultdict(list)

        for _data in json_data:
            city = _data.get('city')
            date = _data.get('date')
            time = _data.get('time')

            filter_data[city].append((date, time))

            temperature = _data.get('temperature')
            weather = _data.get('weather')

            check_temperature_and_weather = self._is_temperature_and_weather_correct(temperature, weather)
            if not check_temperature_and_weather.status:
                return JSONCheckResult(False, check_temperature_and_weather.message)

        if not self._is_data_in_db(filter_data):
            return JSONCheckResult(False, {'message': 'Некоторые данные, которые вы пытаетесь сохранить, уже занесены'})
        return JSONCheckResult(True, '')

    def _is_data_in_db(self, data: defaultdict):
        for city in data.keys():
            date_time_data = data.get(city)
            date = []
            time = []
            for el in date_time_data:
                date.append(el[0])
                time.append(el[1])
            weather_from_db = Weather.objects.filter(
                city=city,
                date__in=date,
                time__in=time,
            )
            return not (bool(len(weather_from_db)))

    def _is_temperature_and_weather_correct(self, temperature: str, weather: str) -> namedtuple:
        WeatherCheckResult = namedtuple('WeatherCheckResult', 'status message')
        try:
            temperature = int(temperature)
        except ValueError as err:
            return WeatherCheckResult(False, {'message': str(err)})

        else:
            if temperature > 0 and weather == 'Снег' or temperature < 0 and weather == 'Дождь':
                return WeatherCheckResult(False, {'message': f'Некорректные данные {temperature} {weather}'})

            return WeatherCheckResult(True, '')

    def _get_filter_params_from_url(self) -> dict:
        '''
        Converts HTTP_REFERER to dictionary with filter params
        '''
        # check that URL has extra parameters and get all parameters from URL
        url = self.request.META['HTTP_REFERER']
        parsed = urlparse.urlparse(url)
        parameters = parse_qs(parsed.query)
        parameters = {f'{k}__in': v for k, v in parameters.items()}
        return parameters


class ImportJsonInfoView(View):
    def get(self, request, *args, **kwargs):
        json_format = [
            {
                "date": "2022-07-01",
                "time": 14,
                "city": "Saint-Petersburg",
                "temperature": 20,
                "weather": "Солнечно"
            },
            {
                "date": "2022-07-01",
                "time": 15,
                "city": "Saint-Petersburg",
                "temperature": 20,
                "weather": "Солнечно"
            }
        ]
        context = f'Для загрузки данных в формате JSON необходимо отправить POST-запрос на ендпоинт ' \
                  f'{HOSTNAME}import/ в формате {json_format}'
        return render(request, 'web_app/import_data_info.html', {'menu': MAIN_MENU, 'context': context})


def custom_page_not_found_view(request, exception):
    return HttpResponseNotFound('Мы не можем найти такую страницу')
