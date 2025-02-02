"""
URL configuration for bharatfd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import yaml

from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from faqs.views import FAQ, SchemaView

from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


class FAQSchema(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        with open("faqs/faqs.yaml", "r") as stream:
            try:
                schema_dict = yaml.safe_load(stream)

            except yaml.YAMLError as exc:
                return JsonResponse(
                    {"error": "Failed to load OpenAPI schema"}, status=500
                )

        schema = super().get_schema(request=request, public=public)
        schema.paths = schema_dict.get("paths", schema.paths)
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="BharatFD Backend Intern",
        default_version="1.0.0",
        description="Documentation for Django APIs",
    ),
    public=True,
    generator_class=FAQSchema,
    authentication_classes=[],
    patterns=[],
)


urlpatterns = [
    path("schema", SchemaView.as_view(), name="schema"),
    path(
        "docs",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("admin/", admin.site.urls),
    path("faqs", csrf_exempt(FAQ.as_view()), name="FAQs"),
]
