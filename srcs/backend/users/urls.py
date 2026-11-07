from django.urls import path
from .views import signup_view, update_profile_view, profile_view, user_detail_view, user_events_view, UserFollowersView, UserFollowingView, chat_contacts_view, user_search_view
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update_profile'),
    path('contacts/', chat_contacts_view, name='user-contacts'), # WIP ALEK
    path('users/search/', user_search_view, name='user-search'), # WIP ALEK
    path('users/<int:user_id>/', user_detail_view, name='user_detail'),
    path('users/<int:user_id>/events/', user_events_view, name='user_events'),
    path('users/<int:user_id>/followers/', UserFollowersView.as_view(), name='user-followers'),
    path('users/<int:user_id>/following/', UserFollowingView.as_view(), name='user-following'),
    path('users/<int:user_id>/contacts/', chat_contacts_view, name='user-contacts'),
]
