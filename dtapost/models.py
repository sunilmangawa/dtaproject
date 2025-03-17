from django.db import models
from django.contrib import admin
import csv
import pandas as pd
from django.db import models
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponse
from django.contrib import messages



# Location-based Models
class State(models.Model):
    state_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.state_name

class Division(models.Model):
    div_name = models.CharField(max_length=100, unique=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.div_name

class District(models.Model):
    dist_name = models.CharField(max_length=100, unique=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)

    def __str__(self):
        return self.dist_name

class Tehsil(models.Model):
    tehsil_name = models.CharField(max_length=100, unique=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return self.tehsil_name

class Village(models.Model):
    AREA_TYPES = [
        ('schedule', 'Schedule'),
        ('non-schedule', 'Non-Schedule'),
        ('shariya', 'Shariya'),
    ]
    vill_name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    tehsil = models.ForeignKey(Tehsil, on_delete=models.CASCADE)
    area = models.CharField(max_length=20, choices=AREA_TYPES)

    def __str__(self):
        return self.vill_name

# Department-based Models
class Department(models.Model):
    dept_name = models.CharField(max_length=100, unique=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.dept_name

class SubDepartment(models.Model):
    sub_dept_name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.sub_dept_name

class OfficeName(models.Model):
    office_name = models.CharField(max_length=100)  # Removed unique=True
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.office_name} ({self.department})"  # Optional: Improved representation

    class Meta:
        unique_together = ('office_name', 'department')  # Enforce combined uniqueness

class Office(models.Model):
    office = models.ForeignKey(OfficeName, on_delete=models.CASCADE)
    office_number = models.IntegerField(unique=True, blank=True, default=None, null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    tehsil = models.ForeignKey(Tehsil, on_delete=models.CASCADE, blank=True, null=True)
    place = models.CharField(max_length=100, unique=False)

    def __str__(self):
        # return self.office + " " + str(self.district)
        return f"{self.office.office_name} {self.district}"

class SubOffice(models.Model):
    name = models.CharField(max_length=100)
    upper_office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, blank=True)
    tehsil = models.ForeignKey(Tehsil, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.name

# Employment-related Models
class Post(models.Model):
    POST_CHOICES = [
        ('jra', 'JRA'),
        ('aao-ii', 'AAO-II'),
        ('aao-i', 'AAO-I'),
    ]
    POST_TYPE_CHOICES = [
        ('cadre', 'Cadre'),
        ('ex-cadre', 'Ex-Cadre'),
    ]
    post_name = models.CharField(max_length=20, choices=(POST_CHOICES))
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default=None)
    post_number = models.PositiveIntegerField()
    in_office = models.ForeignKey(Office, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        # unique_together = ('post_number', 'in_office')  # Unique number per office
        unique_together = ()  # Unique number per office
        ordering = ['in_office', 'post_number']

    def __str__(self):
        return f"{self.get_post_name_display()} ({self.post_number}) - {self.in_office}"
    
    def clean(self):
        if not self.in_office:
            raise ValidationError("Office must be provided for the post.")
        if Office.objects.filter(office__office_name=self.in_office.office.office_name).count() > 1:
            raise ValidationError("Multiple offices with this name exist. Provide district/department in CSV.")    
    # def __str__(self):
    #     return self.post_name

class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    employeeID = models.CharField(max_length=15)
    link_number = models.IntegerField()
    dob = models.DateField()
    mobile = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    home_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    education = models.CharField(max_length=50,null=True)
    current_office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, related_name='current_office')
    # join_office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='joined_office')
    current_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    currentOffice_join_date = models.DateField()
    # apo_posting = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class TransferPrevious(models.Model):
    order_no = models.CharField(max_length=100)
    date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    old_office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='previous_office')
    new_office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='new_office')

    def __str__(self):
        return f"Transfer {self.order_no} - {self.employee.name}"

class History(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    office = models.ManyToManyField(Office)
    from_date = models.DateField()
    to_date = models.DateField()
    duration = models.IntegerField()

    def __str__(self):
        return f"History of {self.employee.name}"

class TransferList(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    current_office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='current_transfer')
    new_office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='new_transfer')

    def __str__(self):
        return f"{self.employee.name} transfer to {self.new_office}"

