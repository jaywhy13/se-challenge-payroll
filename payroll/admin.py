from django.contrib import admin

from payroll.models import (
    Partner, PartnerProfile, EmployeeGroup, EmployeeTime,
    EmployeeTimesheet
)

admin.site.register(Partner)
admin.site.register(PartnerProfile)
admin.site.register(EmployeeGroup)
admin.site.register(EmployeeTimesheet)


class EmployeeTimeAdmin(admin.ModelAdmin):

    list_display = [
        'employee_id', 'start_date', 'end_date',
        'unit', 'quantity', 'timesheet', 'employee_group',
        'rate', 'amount_paid']

    list_filter = [
        'employee_id', 'employee_group', 'timesheet',
        'timesheet__partner_profile',
    ]

    def rate(self, obj):
        return obj.employee_group.rate

    def amount_paid(self, obj):
        return obj.employee_group.rate * obj.quantity

admin.site.register(EmployeeTime, EmployeeTimeAdmin)
