from django.db import models
from rest_framework.exceptions import ValidationError

NULLABLE = {'null': True, 'blank': True}


class PartnerTypes:
    """
    Класс определения типов партнеров-участников.
    """
    MANUFACTURER = 0
    NET = 1
    IE = 2

    TYPES = [(MANUFACTURER, 'Производитель'), (NET, 'Розничная сеть'), (IE, 'Индивидуальный предприниматель')]


class Partner(models.Model):
    """
    Модель партнера сети.
    Типы партнеров-участников определяются классом PartnerTypes.
    Первоначально заданы след. типы: Производитель - 0, Розничная сеть - 1, Индивидуальный предприниматель - 2.
    Иерархия: у производителя всегда 0, у других по возрастанию.
    """

    name = models.CharField(max_length=250, verbose_name='Наименование')
    partner_type = models.PositiveIntegerField(max_length=2, choices=PartnerTypes.TYPES, verbose_name='Тип')
    provider = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='Поставщик', **NULLABLE)
    debt = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Задолженность поставщику', **NULLABLE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    level = models.PositiveIntegerField(verbose_name='Уровень')

    class Meta:
        verbose_name = 'Партнер'
        verbose_name_plural = 'Партнеры'

    def __str__(self):
        return f'Партнер: {self.name}'

    def save(self, *args, **kwargs):
        """
        Процедура устанавливает и сохраняет уровень партнера в иерархии автоматически.
        Если у партнера есть поставщик, тогда его уровень на 1 больше чем у его поставщика
        Если нет поставщика, значит это производитель и будет установлен уровень 0.
        """
        if self.provider:
            self.level = self.provider.level + 1
        else:
            self.level = 0

        super().save(*args, **kwargs)

    def clean(self):
        """
        Проверка корректности уровней партнеров.
        """

        if self.partner_type == PartnerTypes.MANUFACTURER and self.level != 0:
            raise ValidationError("У производителя допускается только нулевой уровень!")
        elif self.partner_type == PartnerTypes.MANUFACTURER and self.provider:
            raise ValidationError("У производителя не может быть поставщика из данной сети")
        elif self.partner_type in [PartnerTypes.NET, PartnerTypes.IE] and self.level == 0:
            raise ValidationError("Партнеры-участники данной сети (кроме производителя) не могут иметь нулевой уровень!")
        super().clean()


class Contacts(models.Model):
    """
    Модель контактов
    """
    partner = models.OneToOneField(Partner, on_delete=models.CASCADE, verbose_name='Партнер')
    email = models.EmailField(verbose_name='E-mail', **NULLABLE)
    country = models.CharField(max_length=50, verbose_name='Страна', **NULLABLE)
    city = models.CharField(max_length=50, verbose_name='Город', **NULLABLE)
    street = models.CharField(max_length=100, verbose_name='Улица', **NULLABLE)
    house_number = models.CharField(max_length=20, verbose_name='Номер дома', **NULLABLE)

    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'Контакты: {self.partner}, E-mail: {self.email}, cтрана: {self.country},  город: {self.city}'


class Product(models.Model):
    """
    Модель продуктов
    """
    name = models.CharField(max_length=250, verbose_name='Наименование')
    model = models.CharField(max_length=100, verbose_name='Модель')
    date_create = models.DateField(verbose_name='Дата выхода')
    owner = models.ForeignKey(Partner, on_delete=models.CASCADE, verbose_name='Владелец')

    class Meta:

        verbose_name = 'Продукция'

    def __str__(self):
        return f'Продукт: {self.name}, модель: {self.model}, владелец: {self.owner}'
