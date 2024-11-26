from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from users.models import User
from nb1school.models import Learners, Leads

class SearchBotTK(models.Model):
    """
    Отображение результатов
    """
    tg_username = models.CharField('Ник TG', null=True, editable=False)
    query_txt = models.CharField('Текст запроса', null=False, editable=False)
    result = models.BooleanField('Результат поиска', null=False, editable=False)

    class Meta:
        verbose_name = _("Поиск ТК")
        verbose_name_plural = _("Поисков ТК")

    def __str__(self):
        return f'{self.tg_username}, - {self.query_txt}, Результат: {self.result}'

class SuppBotTableRequests(models.Model):
    """
    Обращения в саппорт бот
    """
    id = models.BigAutoField(primary_key=True)
    learner = models.ForeignKey(
        Learners,
        verbose_name="Ученик",
        on_delete=models.PROTECT,
        null=True,
        blank=True
        )
    lead = models.ForeignKey(
        Leads,
        verbose_name="Лид",
        on_delete=models.PROTECT,
        null=True,
        blank=True
        )
    first_menu = models.CharField('Направление', editable=False)
    theme = models.CharField('Тема обращения', editable=False)
    messages = models.ManyToManyField('ChatMessages', verbose_name='Сообщения')
    work_eval = models.IntegerField('Оценка ответа', editable=False, null=True)
    feedback = models.CharField('Отзыв об ответе', editable=False, null=True)
    date_start = models.DateTimeField('Дата обращения', editable=False, default=timezone.now)
    date_stop = models.DateTimeField('Дата завершения', editable=False, null=True)
    who_answered = models.ForeignKey(
        User,
        verbose_name="Ответственный",
        on_delete=models.PROTECT,
        null=True,
        blank=True
        )
    statuses = {
        "NEW": "Открыт",
        "INWORK": "В работе",
        "WAITING": "В ожидании",
        "COMPLET": "Выполнен"
    }
    status = models.CharField("Статус", choices=statuses, default="NEW")

    is_new_message = models.BooleanField(
        _('Новое сообщение'),
        default=False,
        help_text=_('Новое сообщение от пользователя')
        )

    is_work = models.BooleanField(
        _('В процессе'),
        default=False,
        help_text=_('Ответственный находится в процессе диалога')
        )

    class Meta:
        verbose_name = _("Обращение в бот")
        verbose_name_plural = _("Обращения в бот")
        #ordering = ['messages__sent']

    def __unicode__(self):
        return f'{self.id}, {self.first_menu}'

    def __str__(self):
        return f'{self.id}, {self.first_menu}'

class FeedBack(models.Model):
    full_name = models.CharField('Имя Фамилия', null=True)
    tg_username = models.CharField('TG_Username', null=True, editable=False)
    tg_userid = models.BigIntegerField('TG_UserID', editable=False)
    date_creat = models.DateField('Дата создания отзыва', editable=False, default=timezone.now)
    messages = models.ManyToManyField('ChatMessages', verbose_name='Сообщения')

    class Meta:
        verbose_name = "Отзыв/Предложение"
        verbose_name_plural = "Отзывы/Предложения"

    def __str__(self):
        return f'{self.full_name}, {self.tg_username}, От: {self.date_creat}'

class ChatMessages(models.Model):
    """
    Все сообщения в бот
    """
    from_who = models.CharField("От кого", null=True)
    tg_userid = models.BigIntegerField('TG_UserID', editable=False, null=True)
    message = models.TextField("Сообщение", null=True)
    image = models.CharField("ID Фото", null=True)
    video = models.CharField("ID Видео", null=True)
    voice = models.CharField("ID Аудио", null=True)
    file = models.CharField("ID Файла", null=True)
    caption = models.CharField("Подпись к файлу", null=True)
    sent = models.DateTimeField("Отправленно", auto_now_add=True)
    edited = models.DateTimeField("Изменено", auto_now=True, null=True)

    class Meta:
        verbose_name = _('Сообщение чата')
        verbose_name_plural = _('Сообщения чата')

    def __str__(self):
        return f'\n{self.from_who}, {self.sent},\n{self.message};'
