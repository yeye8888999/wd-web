from django.conf.urls import include, url

from apps.users import views

urlpatterns = [
    url(r'^register$',views.register,name='register'),
    url(r'^do_register$',views.do_register,name='do_register'),
    url(r'^active/(.+)$',views.ActiveView.as_view(),name='active'),
    url(r'^login$',views.LoginView.as_view(),name='login'),

]