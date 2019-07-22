"""PDG URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
#from django.conf.urls import url
#from django.contrib import admin


from main.views import *
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',HomeView.as_view(),name="home"),
    url(r'^add_inference_rule$',add_inference_rule,name="add_inference_rule"),
    url(r'^add_feed$',add_feed,name="add_feed"),
    url(r'^add_expression$',add_expression,name="add_expression"),
    url(r'^add_connection$',add_connection,name="add_connection"),
    url(r'^add_symbol$',add_symbol,name="add_symbol"),
    ]
