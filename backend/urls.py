# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from documents.views import DocumentViewSet, TransactionListView
from users.views import RegisterView, ProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def chrome_devtools_config(request):
    return JsonResponse({"status": "ok"})
router = routers.DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/', include(router.urls)),
    path('api/transactions/', TransactionListView.as_view(), name='transactions'),
    path('', include('frontend.urls')),
    path('.well-known/appspecific/com.chrome.devtools.json', chrome_devtools_config),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
