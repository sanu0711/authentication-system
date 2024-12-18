from django.urls import path
from . import views
urlpatterns = [
    path('login/',views.sign_in,name="sign_in"),
    path('signup/',views.sign_up,name="sign_up"),
    path('change-password/', views.change_password, name='change_password'),
    path('logout/', views.sign_out, name='sign_out'),
]