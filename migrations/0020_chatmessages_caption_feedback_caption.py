# Generated by Django 5.0.4 on 2024-07-10 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0019_feedback_file_feedback_image_feedback_video_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessages',
            name='caption',
            field=models.CharField(null=True, verbose_name='Подпись к файлу'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='caption',
            field=models.CharField(null=True, verbose_name='Подпись к файлу'),
        ),
    ]
