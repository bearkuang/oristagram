# Generated by Django 5.0.6 on 2024-07-06 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instaapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='site',
            field=models.URLField(blank=True, null=True),
        ),
    ]
