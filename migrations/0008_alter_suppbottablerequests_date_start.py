# Generated by Django 5.0.4 on 2024-07-02 16:29

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0007_alter_suppbottablerequests_work_eval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suppbottablerequests',
            name='date_start',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Дата обращения'),
        ),
    ]
