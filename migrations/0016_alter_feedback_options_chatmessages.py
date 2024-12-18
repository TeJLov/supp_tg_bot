# Generated by Django 5.0.4 on 2024-07-10 14:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0015_feedback_alter_suppbottablerequests_text_question'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='feedback',
            options={'verbose_name': 'Отзыв/Предложение', 'verbose_name_plural': 'Отзывы/Предложения'},
        ),
        migrations.CreateModel(
            name='ChatMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('sent', models.DateTimeField(auto_now_add=True, verbose_name='Отправленно в')),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='messages', to='tg_bot.suppbottablerequests')),
            ],
            options={
                'verbose_name': 'Сообщение чата',
                'verbose_name_plural': 'Сообщения чата',
            },
        ),
    ]
