# coding: utf-8

from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models


# TODO приложение profile
class ExtUser(AbstractUser):
    balans = models.FloatField(u'Баланс', default=0)


class Type(models.Model):
    name = models.CharField(u'Тип задания', max_length=100)


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
    max_count = models.IntegerField(u'Количество запланированных действий')
    count = models.IntegerField(u'Количество выполненных действий')
    description = models.TextField(u'Комментарий')
    create_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUSES, max_length=3)


    def __unicode__(self):
        return