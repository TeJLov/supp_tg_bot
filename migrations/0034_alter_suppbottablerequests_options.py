# Generated by Django 5.0.4 on 2024-08-08 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0033_suppbottablerequests_is_new_message_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='suppbottablerequests',
            options={'ordering': ['messages__sent'], 'verbose_name': 'Обращение в бот', 'verbose_name_plural': 'Обращения в бот'},
        ),
    ]