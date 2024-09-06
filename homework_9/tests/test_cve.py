from datetime import datetime

import pytest

timestamp = datetime.timestamp(datetime.now())

@pytest.mark.asyncio
async def test_create_cve(client):
    cve_data = {
        "id": f"CVE-2024-{timestamp}",
        "date_published": "2024-08-01T12:34:56",
        "date_updated": "2024-08-01T12:34:56",
        "title": "Test CVE",
        "description": "This is a test CVE.",
        "problem_types": [{'descriptions': [{'type': 'text', 'lang': 'en', 'description': 'n/a'}]}]
    }
    response = await client.post("/cves/", json=cve_data)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_cve_by_id(client):
    # Тестуємо отримання CVE за ID
    response = await client.get(f"/cves/CVE-2024-{timestamp}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == f"CVE-2024-{timestamp}"
    assert data["title"] == "Test CVE"

@pytest.mark.asyncio
async def test_search_by_date_range(client):
    # Тестуємо пошук за діапазоном дат
    start_date = "2024-08-01"
    end_date = "2024-08-02"
    response = await client.get(f"/cves/search/date-range?start_date={start_date}&end_date={end_date}")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_search_by_text(client):
    # Тестуємо пошук за текстом
    query = "Test CVE"
    response = await client.get(f"/cves/search/text?query={query}")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_list_cve_with_pagination(client):
    # Тестуємо отримання переліку CVE з пагінацією
    response = await client.get("/cves/?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2

@pytest.mark.asyncio
async def test_create_cve_fail(client):
    cve_data = {
        "id": f"CVE-2024-{timestamp}",
        "date_published": "2024-08-01T12:34:56",
        "date_updated": "2024-08-01T12:34:56",
        "title": [{'descriptions': [{'type': 'text', 'lang': 'en', 'description': 'n/a'}]}],
        "description": "This is a test CVE.",
        "problem_types": [{'descriptions': [{'type': 'text', 'lang': 'en', 'description': 'n/a'}]}]
    }
    response = await client.post("/cves/", json=cve_data)
    assert response.status_code == 422
