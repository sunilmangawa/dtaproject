from django.db import models
from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from .models import State, Division, District, Tehsil, Village, Department, SubDepartment, Office, SubOffice, Post, Employee, TransferPrevious, History, TransferList


def home(request):
    states = State.objects.all()
    districts = District.objects.all()
    employees = Employee.objects.all()
    context = {'states': states, 'districts': districts, 'employees': employees}
    return render(request, 'dtapost/home.html', context)

def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'dtapost/employees.html', {'employees': employees})