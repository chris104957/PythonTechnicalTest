# Origin Markets Backend Test

## How to start this app:

```bash
# install the requirements
pip install -r requirements.txt

# apply migrations
python manage.py migrate

# install fixtures and user account
python manage.py dev_setup

# start the app
python manage.py runserver
```

## Using the app

The `dev_setup` script creates a user account with the username "admin" and 
password "test". For the sake of simplicity, it uses basic auth. 
You can access test the API via the DRF UI at `http://localhost:8000/bonds/` using these credentials.

You can also use it programmatically as follows:
```python
import requests
from urllib.parse import urlencode

# create a new bond
payload = {
    "isin": "RU000A102DV0",
    "size": 400000000,
    "currency": "EUR",
    "maturity": "2027-02-28",
    "lei": "335800O79JS4I4IBD212",
}

response = requests.post(
    'http://localhost:8000/bonds/', json=payload, auth=('admin', 'test')
)
assert response.status_code == 201, response.content

# list objects
response = requests.get(
    'http://localhost:8000/bonds/', auth=('admin', 'test')
)
assert response.status_code == 200, response.content
print(response.json())

# use filters
filters = dict(legal_name='BNP PARIBAS')
response = requests.get(f'http://localhost:8000?{urlencode(filters)}', auth=('admin', 'test'))
assert response.status_code == 200, response.content
print(response.json())
```

## Running the unit tests
```bash
cd origin
pytest . -x --cov --cov-fail-under=100
```

## Other notes
- The API validates that the LEI and ISIN are valid on POST
- The currency must be a valid ISO 4217 currency code
- I've assumed that the LEI is the primary key and must be unique
- Users can only access objects that they themselves have created
- Filtering is possible on all fields of the Bond model

