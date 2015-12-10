from django.conf.urls import patterns, url

from plugin_manager.hosts import views


urlpatterns = patterns('',
                       url(r'^logs/elk.*', views.ProxyElasticSearch.as_view(),
                           name='hosts_logs_elk'),

                       url(r'^$', views.HostList.as_view(),
                           name='hosts_host_list'),
                       url(r'^create$', views.HostCreate.as_view(),
                           name='hosts_host_create'),
                       url(r'^update/(?P<pk>\d+)/', views.HostUpdate.as_view(),
                           name='hosts_host_update'),
                       url(r'^update_plugin/(?P<pk>\d+)/(?P<plugin_name>.*)/', views.HostPluginUpdate.as_view(),
                           name='hosts_host_plugin_update'),
                       url(r'^delete_plugin/(?P<pk>\d+)/(?P<plugin_name>.*)/', views.HostPluginDelete.as_view(),
                           name='hosts_host_plugin_delete'),
                       url(r'^install_plugin/(?P<pk>\d+)/', views.HostPluginInstall.as_view(),
                           name='hosts_host_plugin_install'),
                       url(r'^view/(?P<pk>\d+)/', views.HostDetail.as_view(),
                           name='hosts_host_detail'),
                       url(r'^members/(?P<pk>\d+)/',
                           views.HostMembersList.as_view(),
                           name='hosts_host_members'),
                       url(
                           r'^members/delete/(?P<host_id>\d+)/(?P<user_id>\d+)/',
                           views.HostMembersDelete.as_view(),
                           name='hosts_host_members_delete'),
                       url(r'^membersadd/(?P<pk>\d+)/',
                           views.HostMembersAdd.as_view(),
                           name='hosts_host_members_add'),
                       url(
                           r'^membersaddAjax/(?P<host_id>\d+)/(?P<user_id>\d+)/$',
                           views.HostMemberAdd.as_view(),
                           name='hosts_host_member_add_ajax'),
                       url(r'^delete/(?P<pk>\d+)/', views.HostDelete.as_view(),
                           name='hosts_host_delete'),
                        url(r'^GetVersionsByPluginNameAjax/(?P<plugin_name>.*)/$',
                            views.GetVersionsByPluginNameAjax.as_view(), name='hosts_getversions_by_pluginname'),
                        url(r'^GetVersionsByPluginNameAjax/$',
                            views.GetVersionsByPluginNameAjax.as_view(), name='hosts_getversions_by_pluginname_noparams'),
                        url(r'^HostPluginUpload/(?P<pk>\d+)/',
                            views.HostPluginUpload.as_view(), name='hosts_host_plugin_upload'),
                        url(r'^HostPluginUploadWithName/(?P<pk>\d+)/(?P<plugin_name>.*)/$',
                            views.HostPluginUploadWithName.as_view(), name='hosts_host_plugin_upload_wn'),
)

