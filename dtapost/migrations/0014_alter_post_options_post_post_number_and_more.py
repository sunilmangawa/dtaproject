# Generated by Django 5.1.6 on 2025-03-16 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtapost', '0013_alter_officename_office_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['in_office', 'post_number']},
        ),
        migrations.AddField(
            model_name='post',
            name='post_number',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='post',
            unique_together={('post_number', 'in_office')},
        ),
    ]
