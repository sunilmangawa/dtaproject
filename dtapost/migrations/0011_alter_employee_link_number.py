# Generated by Django 5.1.6 on 2025-03-15 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtapost', '0010_rename_join_date_employee_currentoffice_join_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='link_number',
            field=models.IntegerField(),
        ),
    ]
