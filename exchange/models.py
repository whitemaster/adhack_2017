# coding: utf-8

from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models


# TODO приложение profile
class ExtUser(AbstractUser):
    balans = models.FloatField(u'Баланс', default=0)


class Type(models.Model):
    name = models.CharField(u'Тип задания', max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'тип задания'
        verbose_name_plural = 'Типы задания'


class Task(models.Model):
    STATUS_NEW = "NEW"
    STATUS_CONFIRM = 'CNF'
    STATUS_ACTIVE = "Y"
    STATUS_BLOCKED = "BLC"
    STATUS_DELETED = "DEL"
    STATUS_DONE = "DON"

    STATUSES = (
        (STATUS_NEW, u"Новая"),
        (STATUS_CONFIRM, u"Подтверждена"),
        (STATUS_ACTIVE, u"Активна"),
        (STATUS_BLOCKED, u"Заблокирована модератором"),
        (STATUS_DELETED, u"Удалено"),
        (STATUS_DONE, u'Завершено')
    )

    user = models.ForeignKey(ExtUser, verbose_name=u'Пользователь')
    type = models.ForeignKey(Type, verbose_name=u'Тип')
    price = models.FloatField(u'Цена')
    max_count = models.IntegerField(u'Количество запланированных действий', default=1)
    count = models.IntegerField(u'Количество выполненных действий', default=0)
    description = models.TextField(u'Комментарий', blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUSES, max_length=3, default=STATUS_NEW)
    post_link = models.CharField(u'Отслеживаемый пост', max_length=200, blank=True)

    def __unicode__(self):
        return "{0} {1}".format(self.user, self.create_time)

    class Meta:
        verbose_name = "задача"
        verbose_name_plural = "Задачи"


class ComplitedTask(models.Model):
    """
    Какой пользователь решил какие задачи
    """
    user = models.ForeignKey(ExtUser, related_name='complited')
    task = models.ForeignKey(Task, related_name='complited')