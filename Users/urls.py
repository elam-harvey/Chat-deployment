from django.urls import path
from . import views

urlpatterns = [
    path('join_group/<uuid:group_id>/', views.join_group, name='join_group'),
    path('remove_member/<uuid:group_id>/<int:user_id>/', views.remove_member, name='remove_member'),
    path('chat_room/<uuid:group_id>/', views.chat_room, name='chat_room'),
    path('exit_group/<uuid:group_id>/', views.exit_group, name='exit_group'),
    path('chat_list/', views.chat_list, name='chat_list'),
    path('create_group/', views.create_group, name='create_group'),
    path('group_info/<uuid:group_id>/', views.group_info, name='group_info'),
    path('start_conversation/', views.start_conversation, name='start_conversation'),
    path('direct_message/<int:user_id>/', views.direct_message, name='direct_message'),
    path('send_message/<int:user_id>/', views.send_message, name='send_message'),

    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout, name='logout'),
]