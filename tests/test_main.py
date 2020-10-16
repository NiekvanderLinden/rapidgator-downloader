from main import Client
import responses

BASE_URL = "https://rapidgator.net/api/v2/"


def test_client_init():
    responses.add(
        responses.GET, f"{BASE_URL}user/login",
                  body='{"error": "not found"}', status=404,
                  content_type='application/json'
    )
    Client(username="username", password="password")



