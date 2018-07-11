from django.conf.urls import url
from tradingview import views

urlpatterns = [
    url(r'^$', views.index, name='tradeview_index'),
    url(r'^config$', views.config, name='config'),
    url(r'^symbols$', views.symbols, name='symbols'),
    url(r'^search$', views.search, name='search'),
    url(r'^history$', views.history, name='history'),
    url(r'^time$', views.time, name='time'),
]
