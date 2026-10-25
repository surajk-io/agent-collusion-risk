from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.projects.views import DeliveryReportView, ProjectViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")

urlpatterns = router.urls + [path("reports/delivery/", DeliveryReportView.as_view())]
