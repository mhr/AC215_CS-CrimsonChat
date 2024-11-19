import json
import pytest
from pathlib import Path
from data_pipeline.filter_links import (
    load_links_by_depth,
    get_unique_links,
    normalize_urls,
    filter_urls,
    save_urls,
)


@pytest.fixture
def sample_links_by_depth():
    """Fixture that returns a sample dictionary for testing."""
    return {
        "0": ["https://example.com/page1", "https://example.com/page2"],
        "1": ["https://example.com/page2", "https://example.com/page3/"],
    }


@pytest.fixture
def unwanted_substrings():
    """Fixture that returns a list of unwanted substrings."""
    return [".pdf", ".png", "login", "#"]


def test_load_links_by_depth(tmp_path):
    """Test loading JSON data from a file."""
    file_path = tmp_path / "sample.json"
    data = {"0": ["https://example.com/page1"], "1": ["https://example.com/page2"]}
    with open(file_path, "w") as f:
        json.dump(data, f)

    result = load_links_by_depth(file_path)
    assert result == data
    assert isinstance(result, dict)


def test_get_unique_links(sample_links_by_depth):
    """Test extracting unique links from links by depth."""
    unique_links = get_unique_links(sample_links_by_depth)
    assert unique_links == {
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3/",
    }
    assert len(unique_links) == 3


def test_normalize_urls():
    """Test normalizing URLs by removing trailing slashes."""
    urls = {
        "https://example.com/page1/",
        "https://example.com/page2",
        "https://example.com/page3/",
    }
    normalized = normalize_urls(urls)
    assert normalized == {
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
    }
    assert len(normalized) == 3


def test_filter_urls(unwanted_substrings):
    """Test filtering URLs based on unwanted substrings."""
    urls = [
        "https://example.com/page1.pdf",
        "https://example.com/page2",
        "https://example.com/page3.png",
        "https://example.com/login",
    ]
    filtered = filter_urls(urls, unwanted_substrings)
    assert filtered == ["https://example.com/page2"]
    assert len(filtered) == 1


def test_save_urls(tmp_path):
    """Test saving URLs to a JSON file."""
    urls = ["https://example.com/page1", "https://example.com/page2"]
    file_path = tmp_path / "urls.json"

    save_urls(urls, file_path)

    # Verify the file was created and contains the correct data
    assert file_path.exists()
    with open(file_path, "r") as f:
        data = json.load(f)
    assert data == urls
