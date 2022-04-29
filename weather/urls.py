from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

from weather.settings import DEBUG, STATIC_URL, STATIC_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web_app.urls'))
]

if DEBUG:
    urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)

handler404 = 'web_app.views.custom_page_not_found_view'
