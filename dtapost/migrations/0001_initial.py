# Generated by Django 5.1.6 on 2025-02-12 15:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dist_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('div_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Office',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('office_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dept_name', models.CharField(max_length=100, unique=True)),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.district')),
            ],
        ),
        migrations.AddField(
            model_name='district',
            name='division',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.division'),
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('dob', models.DateField()),
                ('mobile', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('join_date', models.DateField()),
                ('retire_date', models.DateField()),
                ('apo_posting', models.CharField(blank=True, max_length=255, null=True)),
                ('home_district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dtapost.district')),
                ('current_office', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_office', to='dtapost.office')),
                ('join_office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='joined_office', to='dtapost.office')),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_date', models.DateField()),
                ('to_date', models.DateField()),
                ('duration', models.IntegerField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.employee')),
                ('office', models.ManyToManyField(to='dtapost.office')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_name', models.CharField(choices=[('jra', 'JRA'), ('aao-ii', 'AAO-II'), ('aao-i', 'AAO-I')], max_length=20)),
                ('in_office', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dtapost.office')),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='join_post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.post'),
        ),
        migrations.AddField(
            model_name='division',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.state'),
        ),
        migrations.CreateModel(
            name='SubDepartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_dept_name', models.CharField(max_length=100, unique=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.department')),
            ],
        ),
        migrations.AddField(
            model_name='office',
            name='head_office',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dtapost.subdepartment'),
        ),
        migrations.CreateModel(
            name='SubOffice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('head_office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.office')),
            ],
        ),
        migrations.CreateModel(
            name='Tehsil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tehsil_name', models.CharField(max_length=100, unique=True)),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.district')),
            ],
        ),
        migrations.CreateModel(
            name='TransferList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='current_transfer', to='dtapost.office')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.employee')),
                ('new_office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='new_transfer', to='dtapost.office')),
            ],
        ),
        migrations.CreateModel(
            name='TransferPrevious',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.employee')),
                ('new_office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='new_office', to='dtapost.office')),
                ('old_office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='previous_office', to='dtapost.office')),
            ],
        ),
        migrations.CreateModel(
            name='Village',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vill_name', models.CharField(max_length=100)),
                ('area', models.CharField(choices=[('schedule', 'Schedule'), ('non-schedule', 'Non-Schedule'), ('shariya', 'Shariya')], max_length=20)),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.district')),
                ('tehsil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dtapost.tehsil')),
            ],
        ),
    ]
