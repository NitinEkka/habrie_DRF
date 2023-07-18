# serializers.py
from rest_framework import serializers
from .models import Student, AcademicDetail, Parent

class AcademicDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicDetail
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = '__all__'

class ParentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parent
        fields = '__all__'
        
