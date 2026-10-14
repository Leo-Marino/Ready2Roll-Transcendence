from django.urls import path
from .views import signup_view, update_profile_view, profile_view, user_detail_view
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update_profile'),
    path('users/<int:user_id>/', user_detail_view, name='user_detail'),
]
