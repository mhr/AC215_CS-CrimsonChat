"""
This test module verifies critical aspects of the authentication process and 
environment variable loading for integration testing against a deployed backend service.

Overview:
- The `test_auth()` test attempts to log into the backend using the provided 
  password (set as an environment variable in the GitHub Actions workflow) and expects 
  a successful 200 OK response, thereby validating the authentication endpoint.

Pre-requisites:
- Ensure `BACKEND_URL` and `TEST_PASSWORD` are set as environment variables.
- Install dependencies (e.g., `requests`, `pytest`) via:
  
  pip install pytest requests

How to Run:
- Locally:
  export BACKEND_URL="your_backend_url"
  export TEST_PASSWORD="your_test_password"
  pytest tests/integration/

- GitHub Actions:
  Ensure `BACKEND_URL` and `TEST_PASSWORD` are set as repository secrets.

Expected Outcomes:
- `test_auth()`: Passes if the `/login` endpoint returns a 200 OK status and 
  presumably a token or successful login response.
"""

import os
import requests
import pytest

# Fetch the BASE_API_URL from environment variables or use the default if not provided.
BASE_API_URL = os.getenv("BACKEND_URL", "https://api-service-test-692586115434.us-central1.run.app")

# Fixture to obtain and store the auth key
@pytest.fixture(scope="session")
def auth_key():
    """
    Fixture to authenticate and retrieve an auth key for use in all tests.
    """
    auth_url = f"{BASE_API_URL}/login"
    password = os.getenv("TEST_PASSWORD")

    assert password is not None, "TEST_PASSWORD must be set as an environment variable."

    credentials = {"password": password}
    response = requests.post(auth_url, json=credentials)

    assert response.status_code == 200, f"Authentication failed: {response.text}"
    
    # Extract the token from the response (adjust based on API response structure)
    token = response.json()
    assert token is not None, "Auth token not found in login response."
    
    # print("Obtained Auth Key:", token)
    return token


# Test 1: Check if Auth Key is obtained
def test_auth(auth_key):
    """
    Verify that the auth_key fixture returns a valid token.
    """
    assert auth_key is not None, "Auth key should not be None."

def test_llm(auth_key):      
    llm_url= f"{BASE_API_URL}/llm/query"
    user_message = "Tell me about an upcoming CS event?"
    chat_history = None

    payload = {
        "query": user_message,
        "chat_history": [] if chat_history is None else chat_history,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_key["key"]}",
    }

    response = requests.post(llm_url, json=payload, headers=headers)

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    
  