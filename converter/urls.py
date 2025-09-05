from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("operation/<str:operation>/", views.detail_page, name="detail_page"),
    path("convert/<str:operation>/", views.convert, name="convert"),
]
