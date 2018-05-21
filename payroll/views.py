from django.views.generic.base import TemplateView

from rest_framework import viewsets

from payroll.models import Partner

from payroll.serializers import (
    PartnerSerializer, PartnerProfileSerializer,
    EmployeeGroupSerializer, EmployeeTimeSerializer
)


class HomeView(TemplateView):

    template_name = "index.html"


class PartnerViewSet(viewsets.ModelViewSet):

    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
