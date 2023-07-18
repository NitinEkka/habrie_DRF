from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(AcademicDetail)
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(Document)
admin.site.register(Csv)

