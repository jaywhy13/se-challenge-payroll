from io import BytesIO

from django.views.generic.base import TemplateView
from django.views.generic import DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from rest_framework import viewsets

from payroll.models import (
    Partner, PartnerProfile, EmployeeTime,
    EmployeeTimesheet
)
from payroll.forms import TimesheetUploadForm

from payroll.serializers import (
    PartnerSerializer, PartnerProfileSerializer,
    EmployeeGroupSerializer, EmployeeTimeSerializer
)


class HomeView(TemplateView):

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["partners"] = Partner.objects.all()
        return ctx

class PartnerProfilesView(DetailView):

    template_name = "profiles.html"
    model = Partner
    pk_url_kwarg = "partner"
    context_object_name = "partner"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profiles"] = self.get_object().profiles.all()
        return ctx

class PartnerProfileView(FormView, SingleObjectMixin):

    template_name = "profile.html"
    model = PartnerProfile
    pk_url_kwarg = "profile"
    context_object_name = "profile"
    form_class = TimesheetUploadForm

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        ctx = super().get_context_data(**kwargs)
        partner = self.object.partner
        ctx["timesheet_report"] = \
            EmployeeTimesheet.get_timesheet_report(
                partner=partner, partner_profile=self.object)
        return ctx

    def form_valid(self, form):
        partner_profile = self.get_object()
        partner = partner_profile.partner
        csv_file = self.request.FILES["timesheet"]
        report_id, csv_data = \
            EmployeeTimesheet.get_report_id_and_data_from_csv(csv_file)        
        try:
            EmployeeTimesheet.create_timesheet(
                partner=partner,
                partner_profile=partner_profile,
                report_id=report_id,
                data=csv_data,
                source='CSV Upload',
                name='CSV Upload')
            messages.info(self.request, "Successfully created timesheet")
        except Exception as e:
            messages.error(self.request, str(e))
        return redirect(
            reverse("partner-profile",
                    kwargs=dict(partner=partner.pk,
                                profile=partner_profile.pk)))


class PartnerViewSet(viewsets.ModelViewSet):

    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
