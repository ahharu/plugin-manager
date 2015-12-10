from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
import socketio.sdjango

from plugin_manager.core import views


socketio.sdjango.autodiscover()

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^', include('plugin_manager.accounts.urls')),
                       url(r'^$', views.Dashboard.as_view(), name='index'),
                       url(r'^hosts/', include('plugin_manager.hosts.urls')),
                       url(r'^launch-window/',
                           include('plugin_manager.launch_window.urls')),
                       url("^socket\.io", include(socketio.sdjango.urls)),)

# Serve the static files from django
if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^media/(?P<path>.*)$',
                                'django.views.static.serve',
                                {'document_root': settings.MEDIA_ROOT, }),
                            url(r'^static/(?P<path>.*)$',
                                'django.views.static.serve',
                                {'document_root': settings.STATIC_ROOT}),)
