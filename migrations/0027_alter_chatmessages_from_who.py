# Generated by Django 5.0.4 on 2024-07-16 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0026_remove_chatmessages_feedbk_remove_chatmessages_sbtr_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessages',
            name='from_who',
            field=models.CharField(null=True, verbose_name='От кого'),
        ),
    ]