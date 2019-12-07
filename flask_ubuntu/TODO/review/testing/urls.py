#from django.conf.urls import url
#from django.contrib import admin


from main.views import *
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^add_inference_rule$', add_inference_rule, name="add_inference_rule"),
    url(r'^add_feed$', add_feed, name="add_feed"),
    url(r'^add_expression$', add_expression, name="add_expression"),
    url(r'^add_connection$', add_connection, name="add_connection"),
    url(r'^add_symbol$', add_symbol, name="add_symbol"),
]
