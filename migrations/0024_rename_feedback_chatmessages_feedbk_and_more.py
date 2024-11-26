# Generated by Django 5.0.4 on 2024-07-11 13:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0023_remove_feedback_caption_remove_feedback_file_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatmessages',
            old_name='feedback',
            new_name='feedbk',
        ),
        migrations.RemoveField(
            model_name='chatmessages',
            name='chat',
        ),
        migrations.AddField(
            model_name='chatmessages',
            name='sbtr',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sbtr', to='tg_bot.suppbottablerequests', verbose_name='Чат'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='messages',
            field=models.ManyToManyField(null=True, to='tg_bot.chatmessages', verbose_name='Сообщения'),
        ),
    ]
