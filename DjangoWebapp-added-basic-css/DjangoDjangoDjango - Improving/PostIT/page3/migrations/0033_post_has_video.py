# Generated by Django 4.0.6 on 2022-08-23 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page3', '0032_post_has_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='has_video',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
