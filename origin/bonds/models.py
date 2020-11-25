from datetime import date
import os
import requests
from urllib.parse import urlencode

from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def fixed_charfield(length: int = 3):
    """
    Creates a regex validator that ensures charfield is of a given length
    """
    return RegexValidator(
        regex=f'^.{{{length}}}$',
        message=f'This value must be {length} characters long',
        code='invalid_length',
    )


class BondManager(models.Manager):
    def create(
        self, isin: str, size: int, currency: str, maturity: date, lei: str, user: User
    ) -> 'Bond':
        """
        Calculates the legal name from the given lei, and creates and returns Bond instance.
        Assumes that all of the parameters have already been validated.
        """
        base_url = 'https://leilookup.gleif.org/api/v2/leirecords'
        params = dict(lei=lei)

        response = requests.get(f'{base_url}?{urlencode(params)}')
        assert response.status_code == 200, response.text

        result = next(filter(lambda x: x['LEI']['$'] == lei, response.json()), None)
        legal_name = result['Entity']['LegalName']['$']

        return super().create(
            isin=isin,
            user=user,
            size=size,
            currency=currency,
            maturity=maturity,
            lei=lei,
            legal_name=legal_name,
        )


class CurrencyManager(models.Manager):
    def populate(self) -> None:
        """
        Populates the database with all valid ISO 4217 currency codes from the fixtures list
        """
        with open(
            os.path.join(settings.BASE_DIR, 'bonds', 'migrations', 'currencies.csv')
        ) as f:
            for currency in f.readlines():
                self.get_or_create(code=currency.strip())


class Currency(models.Model):
    objects = CurrencyManager()

    code = models.CharField(
        max_length=3, validators=[fixed_charfield()], primary_key=True
    )

    def __str__(self) -> str:
        return self.code


class Bond(models.Model):
    objects = BondManager()
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bonds')
    isin = models.CharField(max_length=12, validators=[fixed_charfield(12)])
    size = models.BigIntegerField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    maturity = models.DateField()
    lei = models.CharField(
        max_length=20, validators=[fixed_charfield(20)], primary_key=True
    )
    legal_name = models.CharField(max_length=100)
