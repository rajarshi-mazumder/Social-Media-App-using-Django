# Generated by Django 4.0.6 on 2022-08-20 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page3', '0019_post_reply_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_reply',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
