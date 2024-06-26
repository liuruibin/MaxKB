"""
URL configuration for apps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  froms my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  froms other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: froms django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.http import HttpResponse
from django.urls import path, re_path, include
from django.views import static
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, status

from common.auth import AnonymousAuthentication
from common.response.result import Result
from smartdoc import settings
from smartdoc.conf import PROJECT_DIR

schema_view = get_schema_view(

    openapi.Info(
        title="Python API",
        default_version='v1',
        description="智能客服平台",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[AnonymousAuthentication]
)

urlpatterns = [
    path("api/", include("users.urls")),
    path("api/", include("dataset.urls")),
    path("api/", include("setting.urls")),
    path("api/", include("application.urls"))
]


def pro():
    # 暴露静态主要是swagger资源
    urlpatterns.append(
        re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    )
    # 暴露ui静态资源
    urlpatterns.append(
        re_path(r'^ui/(?P<path>.*)$', static.serve, {'document_root': os.path.join(settings.STATIC_ROOT, "ui")},
                name='ui'),
    )


if not settings.DEBUG:
    pro()


def page_not_found(request, exception):
    """
    页面不存在处理
    """
    if request.path.startswith("/api/"):
        return Result(response_status=status.HTTP_404_NOT_FOUND, code=404, message="找不到接口")
    else:
        index_path = os.path.join(PROJECT_DIR, 'apps', "static", 'ui', 'index.html')
        if not os.path.exists(index_path):
            return HttpResponse("页面不存在", status=404)
        file = open(index_path, "r", encoding='utf-8')
        content = file.read()
        file.close()
        if request.path.startswith('/ui/chat/'):
            return HttpResponse(content, status=200)
        return HttpResponse(content, status=200, headers={'X-Frame-Options': 'DENY'})


handler404 = page_not_found

urlpatterns += [
    re_path(r'^doc(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
            name='schema-json'),  # 导出
    path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
