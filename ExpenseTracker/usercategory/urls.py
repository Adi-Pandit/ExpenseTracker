from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="usercategory"),
    path('add-category', views.add_category, name="add-category"),
    path('edit-category/<int:id>', views.edit_category, name="edit-category"),
    path('category-delete/<str:id>', views.delete_category, name='category-delete'),
]