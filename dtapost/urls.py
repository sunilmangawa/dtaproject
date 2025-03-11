from django.urls import path, include
from .views import home, employee_list


urlpatterns = [
    path('', home, name='home'),
    path('employees/', employee_list, name='employee_list'),
]
