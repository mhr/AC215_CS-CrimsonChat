# tests/integration/test_api_endpoints.py

"""
This test module verifies critical aspects of the authentication process and 
environment variable loading for integration testing against a deployed backend service.

Overview:
- The tests ensure that environment variables from `.env.test` are correctly loaded 
  into the runtime environment.
- The `test_env_loaded()` test checks that `TEST_PASSWORD` is available, confirming 
  that the `.env.test` file has been successfully read.
- The `test_auth()` test attempts to log into the backend using the retrieved password 
  and expects a successful 200 OK response, thereby validating the authentication endpoint.

Pre-requisites:
- Ensure you have a `.env.test` file placed at the project root (one directory up 
  from `tests/` and another level up from `integration/`).
- The `.env.test` file should contain a line like:
  
  TEST_PASSWORD="your_test_password_here"

- Set the `BACKEND_URL` environment variable or let it default to 
  `https://api-service-test-692586115434.us-central1.run.app` if not provided.
- Install dependencies (e.g., `requests`, `pytest`, `python-dotenv`) via:
  
  pip install pytest requests python-dotenv

How to Run:
- From the project root directory, run:
  
  pytest tests/integration/

Expected Outcomes:
- `test_env_loaded()`: Passes if `TEST_PASSWORD` is loaded from `.env.test`.
- `test_auth()`: Passes if the `/login` endpoint returns a 200 OK status and 
  presumably a token or successful login response.
"""

import os
import requests
import pytest
from dotenv import load_dotenv

# Fetch the BASE_API_URL from environment variables or use the default if not provided.
BASE_API_URL = os.getenv("BACKEND_URL", "https://api-service-test-692586115434.us-central1.run.app")

# Determine the path to the .env.test file in the project root.
# __file__ points to this test file; we go up two directories to reach the project root.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
dotenv_path = os.path.join(project_root, ".env.test")

# Load variables from .env.test into environment variables.
load_dotenv(dotenv_path=dotenv_path)

def test_env_loaded():
    """
    Test that the environment variables are correctly loaded from `.env.test`.

    This test prints out the computed project_root and dotenv_path for debugging purposes,
    then asserts that the `TEST_PASSWORD` environment variable is not None. If this test 
    passes, it confirms that `python-dotenv` successfully loaded the `.env.test` file.
    """
    print("Project Root Directory:", project_root)
    print("Dotenv Path:", dotenv_path)
    assert os.getenv("TEST_PASSWORD") is not None, "TEST_PASSWORD not loaded from .env.test"

def test_auth():
    """
    Test the authentication endpoint using the loaded environment variables.

    Steps:
    1. Construct the `/login` endpoint using `BASE_API_URL`.
    2. Retrieve the `TEST_PASSWORD` from the environment. If None, the test will fail.
    3. Send a POST request with the `password` as JSON payload to the `/login` endpoint.
    4. Check if the response status code is 200. If it's 200, we assume authentication succeeded.
       (Adjust assertions or parse JSON tokens as needed if your endpoint returns a token.)
    5. If the response indicates failure (like 422 or 401), print debugging info and fail the test.

    Note: 
    - If the backend returns a token or other credentials, you can extend this test 
      to parse and validate that token.
    - If the endpoint or password format changes, update `credentials` accordingly.
    """
    auth_url = f"{BASE_API_URL}/login"
    password = os.getenv("TEST_PASSWORD")
    assert password is not None, "TEST_PASSWORD must be set in .env.test."

    credentials = {"password": password}
    response = requests.post(auth_url, json=credentials)

    # Uncomment for debugging if needed:
    # print("Status Code:", response.status_code)
    # print("Headers:", response.headers)
    # print("Response Text:", response.text)

    # Expecting a 200 OK for successful auth. If the backend uses a different logic, adjust this assert.
    assert response.status_code == 200, f"Authentication failed: {response.text}"

    # If needed, you can parse token here if endpoint returns it:
    # token = response.json().get("token")
    # assert token is not None, "No token returned by login endpoint."


# def test_health_endpoint():
#     """
#     Test the health endpoint to ensure the backend service is running.
#     """
#     health_url = f"{BASE_API_URL}/health"
#     response = requests.get(health_url)
    
#     assert response.status_code == 200, f"Health check failed: {response.text}"
#     assert response.json().get("status") == "healthy", "Backend health status is not healthy."

# def test_create_resource(authenticated_header):
#     """
#     Test creating a new resource in the backend.
#     """
#     create_url = f"{BASE_API_URL}/resources"
#     payload = {
#         "name": "Integration Test Resource",
#         "description": "This resource was created during integration testing."
#     }
    
#     response = requests.post(create_url, json=payload, headers=authenticated_header)
    
#     assert response.status_code == 201, f"Resource creation failed: {response.text}"
#     assert response.json().get("name") == "Integration Test Resource", "Resource name does not match."

# def test_fetch_resource(authenticated_header):
#     """
#     Test fetching an existing resource from the backend.
#     """
#     # Assuming resource with ID 1 exists. Adjust as necessary.
#     resource_id = 1
#     fetch_url = f"{BASE_API_URL}/resources/{resource_id}"
    
#     response = requests.get(fetch_url, headers=authenticated_header)
    
#     assert response.status_code == 200, f"Fetching resource failed: {response.text}"
#     assert response.json().get("id") == resource_id, "Fetched resource ID does not match."
#     assert response.json().get("name") is not None, "Resource name is missing."
#     assert response.json().get("description") is not None, "Resource description is missing."
