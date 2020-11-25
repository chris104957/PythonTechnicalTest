from django.urls import path
from bonds.views import BondViewSet

urlpatterns = [path('', BondViewSet.as_view(dict(get='list', post='create')))]
