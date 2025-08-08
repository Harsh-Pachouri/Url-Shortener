from fastapi.testclient import TestClient
from main import app

# Create a TestClient instance using your FastAPI app
client = TestClient(app)

# This is your first test function
def test_read_root():
    # 1. Send a GET request to the "/" endpoint
    response = client.get("/")
    
    # 2. Assert that the HTTP status code is 200 (OK)
    assert response.status_code == 200
    
    # 3. Assert that the JSON response is exactly what you expect
    assert response.json() == {"Welcome!": "This is a URL shortener"}



def test_create_user():
    # 1. Arrange: Create the data for the new user.
    new_user_data = {
        "username": "testuser",
        "password": "testpassword"
    }

    # 2. Act: Send the POST request to your "/register" endpoint.
    response = client.post("/register", json = new_user_data)

    assert response.status_code == 200

    data = response.json()

    # c. Assert that the username in the response data matches "testuser".
    assert data[username]=="testuser"

    # d. Assert that the response data contains an "id" key.
    assert 'id' in data