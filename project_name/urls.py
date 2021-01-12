"""project_name URL Configuration

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

from django.conf.urls import url
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework import routers, permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from app import registration


schema_view = get_schema_view(
   openapi.Info(
      title="Django Template Backend APIs",
      default_version='v1',
      description="List of APIs used in GTM",
      # terms_of_service="https://www.google.com/policies/terms/",
      # contact=openapi.Contact(email="contact@snippets.local"),
      # license=openapi.License(name="BSD License"),
   ),
#    public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),      # Django Jet Urls
    url(r'^admin/', admin.site.urls),
    url(r'^docs/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^docs-swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url('auth/login/', registration.login),
    url('auth/signup/', registration.signup),
    url('auth/forgot-password/', registration.forgot_password),
    url('auth/reset-password/', registration.reset_password)
]

urlpatterns += [

]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()

urlpatterns += router.urls