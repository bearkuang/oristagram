# Generated by Django 5.0.6 on 2024-06-19 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instaapp', '0010_alter_customuser_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(blank=True, default='profile_pics/default_profile_image.png', null=True, upload_to='profile_pics/'),
        ),
    ]
