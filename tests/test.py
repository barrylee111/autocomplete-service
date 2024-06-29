import os
import pytest

from dotenv import load_dotenv
from fastapi.testclient import TestClient
from autocomplete_service.server import app


# For testing code locally
load_dotenv()
client = TestClient(app)
url = os.getenv("FASTAPI_URL")

@pytest.mark.asyncio
async def test_valid_data():
    response = client.get(f'{url}/?q=London&latitude=43.70011&longitude=-79.4163')
    assert response.status_code == 200
    assert 'suggestions' in response.json()

@pytest.mark.asyncio
async def test_longitude_out_of_range_high():
    response = client.get(f'{url}/?q=London&latitude=43.70011&longitude=200')
    assert response.status_code == 400
    assert 'detail' in response.json()
    assert 'Longitude must be between -180 and 180 degrees.' in response.json()['detail']

@pytest.mark.asyncio
async def test_longitude_out_of_range_low():
    response = client.get(f'{url}/?q=London&latitude=43.70011&longitude=-200')
    assert response.status_code == 400
    assert 'detail' in response.json()
    assert 'Longitude must be between -180 and 180 degrees.' in response.json()['detail']

@pytest.mark.asyncio
async def test_latitude_out_of_range_high():
    response = client.get(f'{url}/?q=London&latitude=100&longitude=-79.4163')
    assert response.status_code == 400
    assert 'detail' in response.json()
    assert 'Latitude must be between -90 and 90 degrees.' in response.json()['detail']

@pytest.mark.asyncio
async def test_latitude_out_of_range_low():
    response = client.get(f'{url}/?q=London&latitude=100&longitude=-79.4163')
    assert response.status_code == 400
    assert 'detail' in response.json()
    assert 'Latitude must be between -90 and 90 degrees.' in response.json()['detail']

@pytest.mark.asyncio
async def test_q_missing():
    response = client.get(f'{url}/?latitude=43.70011&longitude=-79.4163')
    assert response.status_code == 422
    assert 'detail' in response.json()
    assert 'Field required' in response.json()['detail'][0]['msg']

@pytest.mark.asyncio
async def test_all_params_missing():
    response = client.get(f'{url}/')
    assert response.status_code == 422
    assert 'detail' in response.json()
    assert 'Field required' in response.json()['detail'][0]['msg']

@pytest.mark.asyncio
async def test_only_longitude_missing():
    response = client.get(f'{url}/?q=London&latitude=43.70011')
    assert response.status_code == 200
    assert 'suggestions' in response.json()

@pytest.mark.asyncio
async def test_only_latitude_missing():
    response = client.get(f'{url}/?q=London&longitude=-79.4163')
    assert response.status_code == 200
    assert 'suggestions' in response.json()

@pytest.mark.asyncio
async def test_longitude_and_latitude_missing():
    response = client.get(f'{url}/?q=London')
    assert response.status_code == 200
    assert 'suggestions' in response.json()

@pytest.mark.asyncio
async def test_wrong_type_latitude():
    response = client.get(f'{url}/?q=London&latitude=invalid&longitude=-79.4163')
    assert response.status_code == 422
    assert 'detail' in response.json()
    assert 'Input should be a valid number, unable to parse string as a number' in response.json()['detail'][0]['msg']

@pytest.mark.asyncio
async def test_wrong_type_longitude():
    response = client.get(f'{url}/?q=London&latitude=43.70011&longitude=invalid')
    assert response.status_code == 422
    assert 'detail' in response.json()
    assert 'Input should be a valid number, unable to parse string as a number' in response.json()['detail'][0]['msg']

@pytest.mark.asyncio
async def test_unknown_location():
    response = client.get(f'{url}/?q=ThisIsNotACity')
    assert response.status_code == 200
    assert 'suggestions' in response.json()
    assert response.json()['suggestions'] == []