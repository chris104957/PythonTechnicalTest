from rest_framework.viewsets import ModelViewSet
from bonds.serializers import BondSerializer


class BondViewSet(ModelViewSet):
    serializer_class = BondSerializer

    def get_queryset(self):
        keynames = ['legal_name', 'currency', 'lei', 'isin', 'size', 'maturity']
        filters = {
            key: self.request.query_params[key]
            for key in keynames
            if key in self.request.query_params
        }
        return self.request.user.bonds.filter(**filters)

    def get_serializer(self, *args, **kwargs):
        kwargs['user'] = self.request.user
        return super().get_serializer(*args, **kwargs)
