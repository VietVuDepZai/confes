from django.urls import path
from . import views

urlpatterns = [
        path('', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),
    path('documents/add/', views.add_document, name='add_document'),
    path('purchase/<int:document_id>/', views.purchase_document, name='purchase_document'),
    path('documents/edit/<int:doc_id>/', views.edit_document, name='edit_document'),
    path('documents/delete/<int:doc_id>/', views.delete_document, name='delete_document'),

    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
]
