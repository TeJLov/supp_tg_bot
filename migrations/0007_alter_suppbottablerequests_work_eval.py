# Generated by Django 5.0.4 on 2024-07-02 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0006_alter_suppbottablerequests_lead_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suppbottablerequests',
            name='work_eval',
            field=models.IntegerField(editable=False, null=True, verbose_name='Оценка ответа'),
        ),
    ]
