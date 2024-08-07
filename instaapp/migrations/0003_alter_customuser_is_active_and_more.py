# Generated by Django 5.0.6 on 2024-07-07 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instaapp', '0002_post_site'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
