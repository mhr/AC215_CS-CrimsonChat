from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import requests
from bs4 import BeautifulSoup
import json

# URL to scrape
url = "https://events.seas.harvard.edu/calendar"

# Send a GET request to the website
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Get the "Last-Modified" header if available
    last_modified = response.headers.get("Last-Modified")
    if last_modified:
        last_modified_datetime = parsedate_to_datetime(last_modified)
        last_modified_datetime = last_modified_datetime.replace(tzinfo=timezone.utc)
        last_modified_iso = last_modified_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        last_modified_iso = None

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the div with id="event_results"
    event_results_div = soup.find("div", id="event_results")

    if event_results_div:
        # Extract all <div class="em-card_text"> within event_results
        card_text_divs = event_results_div.find_all("div", class_="em-card_text")

        # Extract all <script> tags with type="application/ld+json"
        script_tags = event_results_div.find_all("script", type="application/ld+json")

        # Handle the case where the number of <p> and <script> tags do not match
        min_length = min(len(card_text_divs), len(script_tags))

        print(f"Processing {min_length} matching pairs of <p> and <script> tags...")

        # List to store all the processed JSON objects
        processed_data = []

        for i in range(min_length):
            card_text_div = card_text_divs[i]
            script_tag = script_tags[i]

            # Extract all <p class="em-card_event-text"> inside each <div class="em-card_text">
            p_elements = card_text_div.find_all("p", class_="em-card_event-text")

            # Get the combined text from all <p> tags
            p_text = " ".join([p.get_text(strip=True) for p in p_elements])

            # Try parsing the JSON content inside the script tag
            try:
                json_data = json.loads(script_tag.string)  # Parse the JSON content

                # Check if the parsed JSON is a list or a dictionary
                if isinstance(json_data, list):
                    # If it's a list, add 'description' to each object in the list
                    for event_data in json_data:
                        event_data["description"] = p_text
                        processed_data.append(
                            event_data
                        )  # Add each event object to the list
                elif isinstance(json_data, dict):
                    # If it's a dictionary, directly add 'description'
                    json_data["description"] = p_text
                    processed_data.append(
                        json_data
                    )  # Add the single event object to the list
            except json.JSONDecodeError:
                print(f"Error decoding JSON for event.")

        # Save the processed data into a JSON file
        with open("/app/data/dynamic_events_1.json", "w") as json_file:
            json.dump(processed_data, json_file, indent=4)
        print(f"Processed content saved to /app/data/dynamic_events_1.json")

        # Save the file to a gcp bucket
        with open("/app/gcp_dynamic_data/dynamic_events_1.json", "w") as output_file:
            json.dump(processed_data, output_file, indent=4)
        print(f"Processed content saved to /app/gcp_dynamic_data/dynamic_events_1.json")

        # Turn the data into correct format for database ingestion
        big_string = ""
        for event in processed_data:
            for key, value in event.items():
                if isinstance(
                    value, dict
                ):  # If the value is another dictionary, iterate through it
                    big_string += f"{key}:\n"
                    for sub_key, sub_value in value.items():
                        big_string += f"    {sub_key}: {sub_value}\n"
                else:
                    big_string += f"{key}: {value}\n"
            big_string += "\n"  # Add a newline between events for better readability

        # Metadata for the new JSON
        metadata = {
            "last_modified": last_modified_iso,  # Use the actual modified time if available
            "scraped_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),  # Current time in UTC for when it was scraped
            "word_count": len(big_string.split()),  # Count of words in big_string
            "url": "https://events.seas.harvard.edu/calendar",  # Replace this with the actual URL if needed
        }

        # Structure the new JSON data
        output_json = {
            "https://events.seas.harvard.edu/calendar": {
                "text_content": big_string,
                "metadata": metadata,
            },
        }

        # Save the new structure to a JSON file
        with open("/app/data/processed_dynamic_events_1.json", "w") as output_file:
            json.dump(output_json, output_file, indent=4)
        print(f"Processed content saved to /app/data/processed_dynamic_events_1.json")

        with open(
            "/app/gcp_dynamic_data/processed_dynamic_events_1.json", "w"
        ) as output_file:
            json.dump(output_json, output_file, indent=4)
        print(
            f"Processed content saved to /app/gcp_dynamic_data/processed_dynamic_events_1.json"
        )

    else:
        print("The div with id 'event_results' was not found on the page.")
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
