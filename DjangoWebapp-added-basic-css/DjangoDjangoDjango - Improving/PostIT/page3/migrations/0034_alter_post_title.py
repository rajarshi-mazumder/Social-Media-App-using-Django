# Generated by Django 4.0.6 on 2022-09-10 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page3', '0033_post_has_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
