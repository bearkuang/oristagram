# Generated by Django 5.0.6 on 2024-07-17 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instaapp', '0003_alter_customuser_is_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='filter',
            field=models.CharField(default='none', max_length=50),
        ),
    ]
