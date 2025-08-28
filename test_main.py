import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
import os


class TestStaticFiles:
    """Test static file serving"""
    
    def test_read_root_returns_html(self, client: TestClient):
        """Test that root endpoint serves the HTML file"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "LinkSnap" in response.text
    
    def test_static_css_file(self, client: TestClient):
        """Test that CSS file is served correctly"""
        response = client.get("/static/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]
    
    def test_static_js_file(self, client: TestClient):
        """Test that JavaScript file is served correctly"""
        response = client.get("/static/script.js")
        assert response.status_code == 200
        content_type = response.headers["content-type"]
        assert "javascript" in content_type, f"Expected javascript in content-type, got: {content_type}"


class TestUserAuthentication:
    """Test user registration and authentication"""
    
    def test_create_user_success(self, client: TestClient):
        """Test successful user registration"""
        new_user_data = {
            "username": "testuser_from_test",
            "password": "testpassword123"
        }
        response = client.post("/register", json=new_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser_from_test"
        assert "id" in data
        assert "password" not in data  # Password should not be returned
    
    def test_create_user_duplicate_username(self, client: TestClient):
        """Test registration with duplicate username fails"""
        user_data = {
            "username": "test_duplicate",
            "password": "testpassword123"
        }
        # First registration should succeed
        response1 = client.post("/register", json=user_data)
        assert response1.status_code == 200
        
        # Second registration with same username should fail
        response2 = client.post("/register", json=user_data)
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Username already taken"
    
    def test_login_success(self, client: TestClient):
        """Test successful user login"""
        # First register a user
        user_data = {
            "username": "logintest",
            "password": "testpassword123"
        }
        client.post("/register", json=user_data)
        
        # Then try to login
        login_data = {
            "username": "logintest",
            "password": "testpassword123"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials fails"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_wrong_password(self, client: TestClient):
        """Test login with correct username but wrong password"""
        # Register user
        user_data = {
            "username": "wrongpasstest",
            "password": "correctpassword"
        }
        client.post("/register", json=user_data)
        
        # Try login with wrong password
        login_data = {
            "username": "wrongpasstest",
            "password": "wrongpassword"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == 401


class TestURLShortening:
    """Test URL shortening functionality"""
    
    def get_auth_token(self, client: TestClient, username: str = "testuser", password: str = "testpass123"):
        """Helper method to get authentication token"""
        # Register user
        user_data = {"username": username, "password": password}
        client.post("/register", json=user_data)
        
        # Login and get token
        login_data = {"username": username, "password": password}
        response = client.post("/token", data=login_data)
        return response.json()["access_token"]
    
    def test_shorten_url_success(self, client: TestClient):
        """Test successful URL shortening"""
        token = self.get_auth_token(client)
        
        url_data = {"target_url": "https://www.example.com"}
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/shorten", json=url_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "short_key" in data
        assert data["target_url"] == "https://www.example.com"
        assert "id" in data
        assert "owner_id" in data
        assert "clicks" in data
        assert data["clicks"] == 0
    
    def test_shorten_url_unauthorized(self, client: TestClient):
        """Test URL shortening without authentication fails"""
        url_data = {"target_url": "https://www.example.com"}
        
        response = client.post("/shorten", json=url_data)
        assert response.status_code == 401
    
    def test_shorten_url_invalid_token(self, client: TestClient):
        """Test URL shortening with invalid token fails"""
        url_data = {"target_url": "https://www.example.com"}
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.post("/shorten", json=url_data, headers=headers)
        assert response.status_code == 401
    
    def test_shorten_multiple_urls_unique_keys(self, client: TestClient):
        """Test that multiple URLs get unique short keys"""
        token = self.get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        url1_data = {"target_url": "https://www.example1.com"}
        url2_data = {"target_url": "https://www.example2.com"}
        
        response1 = client.post("/shorten", json=url1_data, headers=headers)
        response2 = client.post("/shorten", json=url2_data, headers=headers)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        key1 = response1.json()["short_key"]
        key2 = response2.json()["short_key"]
        
        assert key1 != key2  # Keys should be unique


class TestURLRedirection:
    """Test URL redirection functionality"""
    
    def get_auth_token(self, client: TestClient, username: str = "redirecttest", password: str = "testpass123"):
        """Helper method to get authentication token"""
        user_data = {"username": username, "password": password}
        client.post("/register", json=user_data)
        
        login_data = {"username": username, "password": password}
        response = client.post("/token", data=login_data)
        return response.json()["access_token"]
    
    def test_redirect_success(self, client: TestClient):
        """Test successful URL redirection"""
        token = self.get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a shortened URL
        url_data = {"target_url": "https://www.google.com"}
        response = client.post("/shorten", json=url_data, headers=headers)
        short_key = response.json()["short_key"]
        
        # Test redirection
        redirect_response = client.get(f"/{short_key}", follow_redirects=False)
        assert redirect_response.status_code == 307  # Temporary redirect
        assert redirect_response.headers["location"] == "https://www.google.com"
    
    def test_redirect_nonexistent_key(self, client: TestClient):
        """Test redirection with non-existent key returns 404"""
        response = client.get("/nonexistentkey")
        assert response.status_code == 404
        assert response.json()["detail"] == "URL not found"
    
    def test_redirect_with_favicon_request(self, client: TestClient):
        """Test that favicon.ico request returns 404 (not treated as short key)"""
        response = client.get("/favicon.ico")
        assert response.status_code == 404


class TestDataValidation:
    """Test input validation and edge cases"""
    
    def test_register_empty_username(self, client: TestClient):
        """Test registration with empty username"""
        user_data = {"username": "", "password": "testpass123"}
        response = client.post("/register", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_empty_password(self, client: TestClient):
        """Test registration with empty password"""
        user_data = {"username": "testuser", "password": ""}
        response = client.post("/register", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_shorten_invalid_url_format(self, client: TestClient):
        """Test URL shortening with invalid URL format"""
        # Get auth token
        user_data = {"username": "urltest", "password": "testpass123"}
        client.post("/register", json=user_data)
        login_data = {"username": "urltest", "password": "testpass123"}
        token_response = client.post("/token", data=login_data)
        token = token_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        url_data = {"target_url": "not-a-valid-url"}
        
        # This should still work as we're not validating URL format in backend
        # But in a real app, you might want to add URL validation
        response = client.post("/shorten", json=url_data, headers=headers)
        assert response.status_code == 200


class TestIntegrationFlow:
    """Test complete user flow integration"""
    
    def test_complete_user_flow(self, client: TestClient):
        """Test complete flow: register -> login -> shorten -> redirect"""
        # 1. Register
        user_data = {"username": "flowtest", "password": "testpass123"}
        register_response = client.post("/register", json=user_data)
        assert register_response.status_code == 200
        
        # 2. Login
        login_data = {"username": "flowtest", "password": "testpass123"}
        login_response = client.post("/token", data=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 3. Shorten URL
        headers = {"Authorization": f"Bearer {token}"}
        url_data = {"target_url": "https://www.github.com"}
        shorten_response = client.post("/shorten", json=url_data, headers=headers)
        assert shorten_response.status_code == 200
        short_key = shorten_response.json()["short_key"]
        
        # 4. Test redirect
        redirect_response = client.get(f"/{short_key}", follow_redirects=False)
        assert redirect_response.status_code == 307
        assert redirect_response.headers["location"] == "https://www.github.com"