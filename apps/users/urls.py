from django.conf.urls import include, url

from apps.users import views

urlpatterns = [
    url(r'^registers$',views.register)
]