import pytest
import argparse
import json
from rag_pipeline.utils.config_utils import validate_json, load_config, get_configuration
from unittest.mock import patch

BASE_PATH = "rag_pipeline.utils.config_utils"
"""
Unit tests for the `validate_json` function.

Function Overview:
- Purpose: Validates a JSON file, ensuring it contains a "texts" key with a list of objects, each with specific fields.
- Input:
  - A file path to a JSON file.
- Output:
  - A list of validated objects from the "texts" key.
- Errors:
  - Raises ValueError if:
    - JSON is invalid or missing the "texts" key.
    - "texts" is not a list.
    - Items in "texts" are missing required fields.
  - Raises FileNotFoundError if:
    - File does not exist.
"""

@pytest.fixture
def valid_json(tmp_path):
    """Fixture to create a valid JSON file for testing."""
    content = {"texts": [{"id": 1, "text": "sample", "url": "http://example.com", "timestamp": "2024-01-01"}]}
    file = tmp_path / "valid.json"
    file.write_text(json.dumps(content))
    return str(file)

@pytest.fixture
def invalid_json(tmp_path):
    """Fixture to create an invalid JSON file."""
    file = tmp_path / "invalid.json"
    file.write_text("{invalid_json}")
    return str(file)

def test_validate_json_valid(valid_json):
    """
    Test case: Valid JSON file.
    Expected: Validated list of objects.
    """
    result = validate_json(valid_json)
    assert result == [{"id": 1, "text": "sample", "url": "http://example.com", "timestamp": "2024-01-01"}]

def test_validate_json_invalid_format(invalid_json):
    """
    Test case: Invalid JSON format.
    Expected: ValueError.
    """
    with pytest.raises(ValueError, match="Invalid JSON format"):
        validate_json(invalid_json)

def test_validate_json_missing_file():
    """
    Test case: Missing JSON file.
    Expected: FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        validate_json("missing_file.json")

def test_validate_json_missing_texts_key(tmp_path):
    """
    Test case: Missing 'texts' key in JSON.
    Expected: ValueError.
    """
    content = {"invalid_key": []}
    file = tmp_path / "missing_texts.json"
    file.write_text(json.dumps(content))
    with pytest.raises(ValueError, match="JSON must contain a top-level 'texts' key"):
        validate_json(str(file))

def test_validate_json_invalid_text_structure(tmp_path):
    """
    Test case: Invalid structure in 'texts' key.
    Expected: ValueError.
    """
    content = {"texts": [{"id": 1, "text": "sample"}]}  # Missing 'url' and 'timestamp'
    file = tmp_path / "invalid_structure.json"
    file.write_text(json.dumps(content))
    with pytest.raises(ValueError, match="Each item must have 'id', 'text', 'url', and 'timestamp' fields"):
        validate_json(str(file))


"""
Unit tests for the `load_config` function.

Function Overview:
- Purpose: Load configuration key-value pairs from a text file into a dictionary.
- Input:
  - A file path to a config file.
- Output:
  - A dictionary with config key-value pairs.
- Errors:
  - Raises FileNotFoundError if file is missing.
"""

@pytest.fixture
def valid_config_file(tmp_path):
    """Fixture to create a valid configuration file."""
    content = "key1=value1\nkey2=value2\n# Comment line\nkey3=value3"
    file = tmp_path / "config.txt"
    file.write_text(content)
    return str(file)

def test_load_config_valid(valid_config_file):
    """
    Test case: Valid configuration file.
    Expected: Dictionary with parsed key-value pairs.
    """
    expected = {"key1": "value1", "key2": "value2", "key3": "value3"}
    assert load_config(valid_config_file) == expected

def test_load_config_missing_file():
    """
    Test case: Missing configuration file.
    Expected: FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        load_config("missing_config.txt")
