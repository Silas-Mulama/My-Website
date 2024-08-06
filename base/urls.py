from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('all-topics/', views.topics_page, name='topics'),
    path('all-rooms/', views.rooms_page, name='rooms'),
    path('all-activities/', views.activitiess_page, name='activities'),
    path('create-room/', views.create_room, name='create-room'),
    path('room-room/<str:pk>', views.display_room, name='room-room'),
    path('update-room/<str:pk>', views.update_room, name='update-room'),
    path('delete-room/<str:pk>', views.delete_room, name='delete-room'),
    
    path('delete-message/<str:pk>', views.delete_message, name='delete-message'),
    path('update-message/<str:pk>', views.update_message, name='update-message'),
    path('user-profile/<str:pk>', views.user_profile, name='user-profile'),
    path('update-profile/', views.update_profile, name='update-profile'),
    
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
