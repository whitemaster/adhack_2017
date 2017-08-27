from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from exchange.views import add_task, task_list, task_check

urlpatterns = [
    url(r'^task_check/(?P<task_id>[0-9]+)/(?P<ext_user_id>[0-9]+)/$', task_check, name='task_check'),
    url(r'^add_task/$', add_task, name='add_task'),
    url(r'^$', task_list, name='task_list'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),  # <--
    url(r'^admin/', admin.site.urls),
]