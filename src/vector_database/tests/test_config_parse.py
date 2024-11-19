import pytest
import argparse
from unittest.mock import patch, mock_open
from vector_database.utils.config_utils import load_config, get_configuration

# Define the base path for patching
BASE_PATCH_PATH = "vector_database.utils.config_utils"

# Master docstring
"""
Unit tests for the configuration utility functions.

Functions Overview:
1. load_config:
   - Purpose: Load a configuration from a text file where each line defines a key-value pair.
   - Input: Path to a valid configuration file.
   - Output: Dictionary with configuration values.
   - Errors: Raises FileNotFoundError for invalid file paths or ValueError for malformed lines.

2. get_configuration:
   - Purpose: Combine defaults, a configuration file, and CLI arguments to produce a final configuration dictionary.
   - Input: Command-line arguments and optionally a configuration file.
   - Output: Fully resolved configuration dictionary.
"""

# Tests for `load_config`

def test_load_config_valid_file():
    """
    Test case: Valid configuration file with multiple key-value pairs.
    Input: A text file with valid key=value pairs.
    Expected Output: Dictionary of key-value pairs.
    Why: Verifies correct parsing of valid configuration files.
    """
    config_content = "key1=value1\nkey2=value2\n"
    with patch("builtins.open", mock_open(read_data=config_content)):
        result = load_config("dummy_path")
    assert result == {"key1": "value1", "key2": "value2"}

def test_load_config_empty_file():
    """
    Test case: Empty configuration file.
    Input: An empty text file.
    Expected Output: Empty dictionary.
    Why: Ensures the function can handle empty files gracefully.
    """
    with patch("builtins.open", mock_open(read_data="")):
        result = load_config("dummy_path")
    assert result == {}

def test_load_config_malformed_line():
    """
    Test case: Malformed line in configuration file.
    Input: A text file with a malformed line.
    Expected Output: ValueError.
    Why: Ensures the function raises an error for invalid formats.
    """
    config_content = "key1=value1\nmalformed_line\n"
    with patch("builtins.open", mock_open(read_data=config_content)):
        with pytest.raises(ValueError):
            load_config("dummy_path")

def test_load_config_file_not_found():
    """
    Test case: Non-existent configuration file.
    Input: Invalid file path.
    Expected Output: FileNotFoundError.
    Why: Ensures the function handles missing files properly.
    """
    with pytest.raises(FileNotFoundError):
        load_config("non_existent_file")


# Tests for `get_configuration`

@patch(f"{BASE_PATCH_PATH}.parse_arguments")
@patch(f"{BASE_PATCH_PATH}.load_config")
def test_get_configuration_with_file_and_args(mock_load_config, mock_parse_arguments):
    """
    Test case: Combination of defaults, file-based config, and CLI arguments.
    Input: File config with overrides from CLI arguments.
    Expected Output: Fully resolved configuration dictionary.
    Why: Validates merging of inputs with correct precedence.
    """
    mock_parse_arguments.return_value = argparse.Namespace(
        config="dummy_config",
        embedding_model="textembedding-gecko@002",
        chunking_method=None,
        chunk_size=1000,
        chunk_overlap=200,
        vector_dim=None,
        testing_json=None,
        bucket_file_path=None,
    )
    mock_load_config.return_value = {"embedding_model": "file_model", "vector_dim": "768"}

    result = get_configuration()
    print(result)
    expected = {
        'query': None,
        'testing_json': None,
        'embedding_model': 'textembedding-gecko@002',
        'chunking_method': 'simple',
        'qdrant_collection': 'cs-crimsonchat-ms2',
        'breakpoint_threshold_type': None,
        'buffer_size': None,
        'breakpoint_threshold_amount': None,
        'chunk_size': 1000,
        'chunk_overlap': 200,
        'vector_dim': 768,
        'bucket_file_path': None,
        'config': 'dummy_config',
    }
    assert result == expected

@patch(f"{BASE_PATCH_PATH}.parse_arguments")
def test_get_configuration_defaults_only(mock_parse_arguments):
    """
    Test case: Only defaults are used (no file or CLI arguments).
    Input: No config file or CLI arguments provided.
    Expected Output: Default configuration dictionary.
    Why: Ensures the function correctly returns defaults when no overrides are provided.
    """
    mock_parse_arguments.return_value = argparse.Namespace(
        config=None,
        embedding_model=None,
        chunking_method=None,
        chunk_size=None,
        chunk_overlap=None,
        vector_dim=None,
        testing_json=None,
        bucket_file_path=None,
    )

    result = get_configuration()
    expected = {
        'query': None,
        'testing_json': None,
        'embedding_model': 'textembedding-gecko@001',
        'chunking_method': 'simple',
        'qdrant_collection': 'cs-crimsonchat-ms2',
        'breakpoint_threshold_type': None,
        'buffer_size': None,
        'breakpoint_threshold_amount': None,
        'chunk_size': None,
        'chunk_overlap': None,
        'vector_dim': 768,
        'bucket_file_path': None,
    }
    assert result == expected
