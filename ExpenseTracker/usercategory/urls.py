from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="usercategory"),
    path('add-category', views.add_category, name="add-category"),
    path('category-delete/<slug:id>', views.delete_category, name='category-delete'),
]