from django.contrib import admin
from .models import Coffee, Report


class CoffeeAdmin(admin.ModelAdmin):
    list_display = ["name", "price"]


class ReportAdmin(admin.ModelAdmin):
    list_display = ["name", "price"]


admin.site.register(Coffee, CoffeeAdmin)
admin.site.register(Report, ReportAdmin)
