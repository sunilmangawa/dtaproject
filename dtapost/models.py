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

class Office(models.Model):
    office_name = models.CharField(max_length=100, unique=True)
    office_id = models.IntegerField(unique=True, blank=True, default=None, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    place = models.CharField(max_length=100, unique=False)

    def __str__(self):
        return self.office_name

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
    in_office = models.ForeignKey(Office, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.post_name

class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    employeeID = models.CharField(max_length=15)
    link_number = models.IntegerField(max_length=7)
    dob = models.DateField()
    mobile = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    home_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    join_office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='joined_office')
    join_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    join_date = models.DateField()
    retire_date = models.DateField()
    apo_posting = models.CharField(max_length=255, blank=True, null=True)
    current_office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, related_name='current_office')

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

