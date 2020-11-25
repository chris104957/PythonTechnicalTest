from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    ValidationError,
)
from stdnum import isin, lei, exceptions
from bonds.models import Bond, Currency


class BondSerializer(ModelSerializer):
    def validate_lei(self, value):
        try:
            return lei.validate(value)
        except exceptions.InvalidChecksum:
            raise ValidationError(f'{value} is not a valid LEI')

    def validate_isin(self, value):
        try:
            return isin.validate(value)
        except exceptions.InvalidChecksum:
            raise ValidationError(f'{value} is not a valid ISIN')

    currency = PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        error_messages={'does_not_exist': '{pk_value} is not a valid currency'},
    )

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = self.user
        return data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Bond
        exclude = ('user',)
        read_only_fields = ('legal_name',)
