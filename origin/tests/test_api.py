import pytest
from urllib.parse import urlencode
from bonds.models import Currency, Bond


@pytest.mark.django_db
def test_create_bond(client):
    """
    Valid bond creation should return a 201 response, and the legal name should be BNP PARIBAS
    """
    payload = {
        "isin": "FR0000131104",
        "size": 100000000,
        "currency": "EUR",
        "maturity": "2025-02-28",
        "lei": "R0MUWSFPU8MPRO8K5P83",
    }
    response = client.post('/bonds/', data=payload)
    assert response.status_code == 201, response.content

    response = client.get('/bonds/')
    assert response.status_code == 200, response.content
    assert len(response.json()) == 1

    bond = Bond.objects.first()
    assert bond.legal_name == 'BNP PARIBAS'


@pytest.mark.django_db
def test_duplicate_entry(client):
    """
    LEI is a primary key - attempting to create two bonds with the same LEI should return a 400 response
    """
    payload = {
        "isin": "FR0000131104",
        "size": 100000000,
        "currency": "EUR",
        "maturity": "2025-02-28",
        "lei": "R0MUWSFPU8MPRO8K5P83",
    }
    response = client.post('/bonds/', data=payload)
    assert response.status_code == 201, response.content

    response = client.post('/bonds/', data=payload)
    assert response.status_code == 400, response.content
    assert response.json()['lei'] == ['bond with this lei already exists.']


@pytest.mark.django_db
def test_invalid_lei(client):
    """
    Test to ensure that a 400 response is returned when LEI is too short or invalid
    """
    payload = {
        "isin": "FR0000131104",
        "size": 100000000,
        "currency": "EUR",
        "maturity": "2025-02-28",
        "lei": "NO",
    }
    response = client.post('/bonds/', data=payload)
    assert response.status_code == 400, response.content
    assert response.json()['lei'] == ["This value must be 20 characters long"]

    payload['lei'] = 'NOOOOOOOOOOOOOOOOOPE'  # 20 characters now
    response = client.post('/bonds/', data=payload)
    assert response.status_code == 400, response.content
    assert response.json()['lei'] == ["NOOOOOOOOOOOOOOOOOPE is not a valid LEI"]


@pytest.mark.django_db
def test_invalid_isin(client):
    """
    Test to ensure that a 400 response is returned when ISIN is too short or invalid
    """
    payload = {
        "isin": "NOOOOOOOOPE",
        "size": 100000000,
        "currency": "EUR",
        "maturity": "2025-02-28",
        "lei": "R0MUWSFPU8MPRO8K5P83",
    }
    response = client.post('/bonds/', data=payload)
    assert response.status_code == 400, response.content
    assert response.json()['isin'] == ["This value must be 12 characters long"]

    payload['isin'] = 'NOOOOOOOOOPE'  # 12 characters now
    response = client.post('/bonds/', data=payload)
    assert response.status_code == 400, response.content
    assert response.json()['isin'] == ["NOOOOOOOOOPE is not a valid ISIN"]


@pytest.mark.django_db
def test_invalid_currency(client):
    """
    Test with an invalid currency should return a 400 response
    """
    payload = {
        "isin": "FR0000131104",
        "size": 100000000,
        "currency": "XXX",
        "maturity": "2025-02-28",
        "lei": "R0MUWSFPU8MPRO8K5P83",
    }
    response = client.post('/bonds/', data=payload)
    assert response.status_code == 400, response.content
    assert response.json()['currency'] == ["XXX is not a valid currency"]


@pytest.mark.django_db
def test_currency_fixtures():
    """
    Test that currency fixture loader works OK
    """
    Currency.objects.populate()
    assert Currency.objects.all().count() == 162
    first = Currency.objects.first()
    assert str(first) == first.code


@pytest.mark.django_db
def test_filtering(client):
    payloads = [
        {
            "isin": "FR0000131104",
            "size": 100000000,
            "currency": "EUR",
            "maturity": "2024-02-28",
            "lei": "R0MUWSFPU8MPRO8K5P83",
        },
        {
            "isin": "RU000A102E37",
            "size": 200000000,
            "currency": "USD",
            "maturity": "2025-02-28",
            "lei": "3003000G7W1O14CJXY62",
        },
        {
            "isin": "RU000A102DZ1",
            "size": 300000000,
            "currency": "GBP",
            "maturity": "2026-02-28",
            "lei": "984500UB306697672C56",
        },
        {
            "isin": "RU000A102DV0",
            "size": 400000000,
            "currency": "EUR",
            "maturity": "2027-02-28",
            "lei": "335800O79JS4I4IBD212",
        },
    ]
    for payload in payloads:
        response = client.post('/bonds/', data=payload)
        assert response.status_code == 201, response.content

    # filter on ISIN
    filters = dict(isin='RU000A102DV0')
    response = client.get(f'/bonds/?{urlencode(filters)}')
    assert response.status_code == 200, response.content
    assert response.json()[0]['lei'] == '335800O79JS4I4IBD212'

    # filter on size
    filters = dict(size=300000000)
    response = client.get(f'/bonds/?{urlencode(filters)}')
    assert response.status_code == 200, response.content
    assert response.json()[0]['lei'] == '984500UB306697672C56'

    # filter on currency
    filters = dict(currency='EUR')
    response = client.get(f'/bonds/?{urlencode(filters)}')
    assert response.status_code == 200, response.content
    assert len(response.json()) == 2

    # filter on maturity
    filters = dict(maturity='2025-02-28')
    response = client.get(f'/bonds/?{urlencode(filters)}')
    assert response.status_code == 200, response.content
    assert response.json()[0]['lei'] == '3003000G7W1O14CJXY62'

    # filter on lei
    filters = dict(lei='R0MUWSFPU8MPRO8K5P83')
    response = client.get(f'/bonds/?{urlencode(filters)}')
    assert response.status_code == 200, response.content
    assert response.json()[0]['lei'] == 'R0MUWSFPU8MPRO8K5P83'

    # filter on legal name
    filters = dict(legal_name='ASLAM CONSULTING AS')
    response = client.get(f'/bonds/?{urlencode(filters)}')
    assert response.status_code == 200, response.content
    assert response.json()[0]['lei'] == '984500UB306697672C56'


@pytest.mark.django_db
def test_multi_user(client, alt_user_client):
    """
    Create a Bond with one user, make sure the other can't get to it
    """
    payload = {
        "isin": "FR0000131104",
        "size": 100000000,
        "currency": "EUR",
        "maturity": "2025-02-28",
        "lei": "R0MUWSFPU8MPRO8K5P83",
    }
    response = alt_user_client.post('/bonds/', data=payload)
    assert response.status_code == 201, response.content

    response = client.get('/bonds/')
    assert response.status_code == 200, response.content
    assert len(response.json()) == 0
