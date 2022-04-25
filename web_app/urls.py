from django.conf.urls.static import static
from django.urls import path

from weather import settings
from web_app.views import MainPageView, WeatherListView, DashboardView, WeatherJsonView, WeatherDetailView, \
    WeatherDeleteView, WeatherCreateView, WeatherUpdateView, WeatherEditorView, ImportJsonInfoView


urlpatterns = [
    path('', MainPageView.as_view(), name='index'),
    path('weather/', WeatherListView.as_view(), name='weather_list'),
    path('weather/<int:pk>', WeatherDetailView.as_view(), name='weather_detail'),
    path('weather/create/', WeatherCreateView.as_view(), name='weather_create'),
    path('weather/<int:pk>/update/', WeatherUpdateView.as_view(), name='weather_update'),
    path('weather/<int:pk>/delete/', WeatherDeleteView.as_view(), name='weather_delete'),

    path('editor/', WeatherEditorView.as_view(), name='editor'),

    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('import/', WeatherJsonView.as_view(), name='import_data'),
    path('import_info/', ImportJsonInfoView.as_view(), name='import_data_info'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
