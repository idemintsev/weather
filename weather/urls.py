from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web_app.urls'))
]

handler404 = 'web_app.views.custom_page_not_found_view'
