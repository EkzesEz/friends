# Generated by Django 4.2.1 on 2023-05-08 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friendship', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='username',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
