from django.contrib import admin
from .models import CarMake, CarModel


# Register your models here.
# CarModelInline class
class CarModelInline(admin.StackedInline):
    model=CarModel
    extra=10

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display=["car_make", "name", "dealer_id", "car_type", "year"]  

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    list_display=["name", "description"]
    inlines=[CarModelInline]

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)