from rest_framework.serializers import ModelSerializer

from payroll.models import (
    Partner, PartnerProfile, EmployeeGroup, EmployeeTime,
)


class PartnerSerializer(ModelSerializer):

    class Meta:
        model = Partner
        fields = ('name',)


class PartnerProfileSerializer(ModelSerializer):

    class Meta:
        model = PartnerProfile
        fields = ('name', 'date_format', 'country', 'pay_period')


class EmployeeGroupSerializer(ModelSerializer):

    class Meta:
        model = EmployeeGroup
        fields = ['name', 'rate', 'partner_profile']


class EmployeeTimeSerializer(ModelSerializer):

    class Meta:
        model = EmployeeTime
        fields = ('start_date', 'end_date', 'unit', 'quantity', 'timesheet')
