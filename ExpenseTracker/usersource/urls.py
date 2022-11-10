from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="usersource"),
    path('add-source', views.add_source, name="add-source"),
    path('source-delete/<slug:id>', views.delete_source, name='source-delete'),
]