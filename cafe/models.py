from typing import List

from django.db import models


class OrderManager(models.Manager):
    @staticmethod
    def calc_price(items: List['Item']) -> int:
        return sum(item.price for item in items)

    def create(self, table_number: int, items: List['Item'], status: str | None = None) -> 'Order':
        if status:
            order = self.model(table_number=table_number, total_price=self.calc_price(items), status=status)
        else:
            order = self.model(table_number=table_number, total_price=self.calc_price(items))
        order.full_clean()
        order.save(using=self._db)
        order.items.set(items)
        return order


class Order(models.Model):
    class Status(models.TextChoices):
        WAIT = "WAIT", "В ожидании"
        READY = "READY", "Готово"
        PAID = "PAID", "Оплачено"

    table_number = models.PositiveIntegerField(verbose_name='Номер стола')
    items = models.ManyToManyField('Item', related_name='orders', verbose_name='Заказы')
    total_price = models.PositiveIntegerField(verbose_name='Итоговая цена')
    status = models.CharField(max_length=5, choices=Status, default=Status.WAIT, verbose_name='Статус')
    created = models.DateTimeField(auto_now_add=True)

    objects = OrderManager()


class Item(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название блюда')
    price = models.PositiveIntegerField(verbose_name='Цена')

    def __str__(self):
        return self.name
