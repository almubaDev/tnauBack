# Generated by Django 5.2 on 2025-04-09 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_userprofile_fecha_reset_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='fecha_reset',
            field=models.DateField(auto_now_add=True),
        ),
    ]
