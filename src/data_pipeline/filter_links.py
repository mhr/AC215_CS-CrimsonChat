import json
from typing import List, Set


def load_links_by_depth(file_path: str) -> dict:
    """Loads a JSON file containing links categorized by depth.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: A dictionary where keys are depths and values are lists of URLs.
    """
    with open(file_path, "r") as file:
        return json.load(file)


def get_unique_links(links_by_depth: dict) -> Set[str]:
    """Extracts all unique links from a dictionary of links categorized by depth.

    Args:
        links_by_depth (dict): A dictionary with depths as keys and lists of URLs as values.

    Returns:
        Set[str]: A set of unique URLs.
    """
    all_unique_links = set()
    for depth, links in links_by_depth.items():
        unique_links = set(links) - all_unique_links
        all_unique_links.update(unique_links)
        print(f"Depth {depth}: {len(unique_links)} unique links")
    print(f"Total unique links: {len(all_unique_links)}")
    return all_unique_links


def normalize_urls(urls: Set[str]) -> Set[str]:
    """Normalizes URLs by removing any trailing slashes.

    Args:
        urls (Set[str]): A set of URLs to normalize.

    Returns:
        Set[str]: A set of normalized URLs.
    """
    return {url.rstrip("/") for url in urls}


def filter_urls(urls: List[str], unwanted_substrings: List[str]) -> List[str]:
    """Filters out URLs containing any of the unwanted substrings.

    Args:
        urls (List[str]): List of URLs to filter.
        unwanted_substrings (List[str]): Substrings to exclude from URLs.

    Returns:
        List[str]: A sorted list of filtered URLs.
    """
    filtered_urls = [
        url
        for url in urls
        if all(unwanted not in url for unwanted in unwanted_substrings)
    ]
    return sorted(set(filtered_urls))


def save_urls(urls: List[str], file_path: str):
    """Saves a list of URLs to a JSON file.

    Args:
        urls (List[str]): The list of URLs to save.
        file_path (str): The path to the JSON file.
    """
    with open(file_path, "w") as file:
        json.dump(urls, file, indent=4)


def main():
    # Load links by depth
    links_by_depth = load_links_by_depth("/app/data/harvard_cs_links_by_depth_0.json")

    # Get all unique links
    all_unique_links = get_unique_links(links_by_depth)

    # Normalize URLs to handle trailing slashes
    normalized_urls = normalize_urls(all_unique_links)

    # Filter unwanted URLs
    unwanted_substrings = [
        ".hqx",
        "Pyret_Style_Guide",
        "mailto:",
        "#h.",
        ".key",
        ".rkt",
        ".pptx",
        ".ppt",
        ".pdf",
        "php#",
        ".gz",
        ".gif",
        "#",
        ".zip",
        ".png",
        ".jpg",
        ".ps",
        "login",
        "signin",
        ".py",
        ".sty",
        ".bib",
        ".shtml",
        "/images/",
        "/Videos",
        ".m",
        ".java",
        ".txt",
        ".tex",
        "/results/",
        "share=",
        "google.com/",
        "https://twitter.com/",
        "http://www.facebook.com/",
        ".doc",
        "binaries",
        ".tgz",
        "logout",
        "BorealisDemo",
        ".js",
        ".als",
        ".bz2",
        ".xlsx",
        ".dvi",
        ".plt",
        " ",
        ".swf",
        ".scm",
        "pyret",
        ".PDF",
        ".ppsx",
        ".git",
        "https://aizenberglab.seas.harvard.edu/media-gallery/detail",
        "Mailto:",
    ]
    filtered_urls = filter_urls(list(normalized_urls), unwanted_substrings)
    print(len(filtered_urls))

    # Save filtered URLs to multiple paths
    save_urls(filtered_urls, "/app/data/harvard_cs_filtered_links.json")
    save_urls(filtered_urls, "/app/gcp_static_data/harvard_cs_filtered_links.json")


if __name__ == "__main__":
    main()
