from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import json
import os

# URL to scrape
URL = "https://events.seas.harvard.edu/calendar"


def fetch_webpage(url):
    """
    Sends a GET request to the specified URL.

    Args:
        url (str): The URL to fetch.

    Returns:
        requests.Response: The response object from the GET request.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    return response


def get_last_modified(headers):
    """
    Extracts and formats the 'Last-Modified' header if available.

    Args:
        headers (requests.structures.CaseInsensitiveDict): HTTP headers from the response.

    Returns:
        str or None: The ISO 8601 formatted last modified time or None if unavailable.
    """
    last_modified = headers.get("Last-Modified")
    if last_modified:
        last_modified_datetime = parsedate_to_datetime(last_modified)
        last_modified_datetime = last_modified_datetime.replace(tzinfo=timezone.utc)
        return last_modified_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def parse_events(soup):
    """
    Parses events from the BeautifulSoup object.

    Args:
        soup (BeautifulSoup): Parsed HTML content.

    Returns:
        list: A list of event data dictionaries.
    """
    event_results_div = soup.find("div", id="event_results")
    if not event_results_div:
        print("The div with id 'event_results' was not found on the page.")
        return []

    card_text_divs = event_results_div.find_all("div", class_="em-card_text")
    script_tags = event_results_div.find_all("script", type="application/ld+json")
    min_length = min(len(card_text_divs), len(script_tags))

    processed_data = []
    for i in range(min_length):
        card_text_div = card_text_divs[i]
        script_tag = script_tags[i]

        # Extract event description
        p_elements = card_text_div.find_all("p", class_="em-card_event-text")
        p_text = " ".join([p.get_text(strip=True) for p in p_elements])

        # Parse JSON data from script tag
        try:
            json_data = json.loads(script_tag.string)
            if isinstance(json_data, list):
                for event_data in json_data:
                    event_data["description"] = p_text
                    processed_data.append(event_data)
            elif isinstance(json_data, dict):
                json_data["description"] = p_text
                processed_data.append(json_data)
        except json.JSONDecodeError:
            print("Error decoding JSON for event.")

    return processed_data


def save_json_data(file_path, data):
    """
    Saves data to a JSON file.

    Args:
        file_path (str): The file path where JSON data will be saved.
        data (dict or list): The data to be saved in JSON format.
    """
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Processed content saved to {file_path}")


def format_for_database(processed_data):
    """
    Formats processed data for database ingestion.

    Args:
        processed_data (list): List of event data dictionaries.

    Returns:
        str: A formatted string for database ingestion.
    """
    big_string = ""
    for event in processed_data:
        for key, value in event.items():
            if isinstance(value, dict):
                big_string += f"{key}:\n"
                for sub_key, sub_value in value.items():
                    big_string += f"    {sub_key}: {sub_value}\n"
            else:
                big_string += f"{key}: {value}\n"
        big_string += "\n"
    return big_string


def create_metadata(last_modified_iso, big_string):
    """
    Creates metadata for the scraped data.

    Args:
        last_modified_iso (str): The last modified date in ISO 8601 format.
        big_string (str): The formatted string for database ingestion.

    Returns:
        dict: Metadata for the JSON output.
    """
    return {
        "last_modified": last_modified_iso,
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "word_count": len(big_string.split()),
        "url": URL,
    }


def main():
    # Fetch webpage content
    response = fetch_webpage(URL)
    if response.status_code != 200:
        return

    # Get last modified date if available
    last_modified_iso = get_last_modified(response.headers)

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    processed_data = parse_events(soup)

    # Save processed data
    save_json_data("/app/data/dynamic_events_1.json", processed_data)
    save_json_data("/app/gcp_dynamic_data/dynamic_events_1.json", processed_data)

    # Format data for database ingestion
    big_string = format_for_database(processed_data)

    # Create metadata
    metadata = create_metadata(last_modified_iso, big_string)
    output_json = {
        URL: {
            "text_content": big_string,
            "metadata": metadata,
        }
    }

    # Save formatted data with metadata
    save_json_data("/app/data/processed_dynamic_events_1.json", output_json)
    save_json_data("/app/gcp_dynamic_data/processed_dynamic_events_1.json", output_json)


if __name__ == "__main__":
    main()
