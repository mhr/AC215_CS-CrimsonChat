from datetime import datetime, timezone
import re
import scrapy
import json
from email.utils import parsedate_to_datetime


with open("/app/data/harvard_cs_filtered_links.json", "r") as file:
    links_by_depth = json.load(file)
    urls = links_by_depth[:10]


class MySpider(scrapy.Spider):
    name = "myspider"

    # List of URLs to scrape
    start_urls = urls

    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.scraped_data = {}  # Initialize an empty dictionary to store scraped data
        self.scraped_text = ""

    def parse(self, response):

        url_dict = {}
        metadata = {}

        last_modified = response.headers.get("Last-Modified")
        if last_modified:
            try:
                # Ensure it's a string and pass it to the parser
                if isinstance(last_modified, bytes):
                    last_modified = last_modified.decode(
                        "utf-8"
                    )  # Decode if it's in bytes

                # Convert Last-Modified header to a datetime object
                last_modified_datetime = parsedate_to_datetime(last_modified)
                last_modified_datetime = last_modified_datetime.replace(
                    tzinfo=timezone.utc
                )

                # Format the datetime to the desired ISO 8601 format with "Z" for UTC
                last_modified_iso = last_modified_datetime.strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )
                metadata["last_modified"] = last_modified_iso

            except (TypeError, ValueError) as e:
                # Handle cases where parsing fails due to an invalid format
                print(f"Error parsing Last-Modified header: {e}")
                metadata["last_modified"] = None
        else:
            metadata["last_modified"] = None

        # For scraped_at (assuming UTC for consistency)
        scraped_at_datetime = datetime.now(timezone.utc)

        # Format the datetime to the desired ISO 8601 format with "Z" for UTC
        scraped_at_iso = scraped_at_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        metadata["scraped_at"] = scraped_at_iso

        text_content = response.xpath(
            """
            //body//*[not(self::script or self::style or self::link or self::meta
                        or self::div[@id="header"] or self::div[@id="footer"]
                        or self::ul[@id="navbar2"] or self::ul[@id="navbar3"])
                and not(ancestor::div[@id="header"] or ancestor::div[@id="footer"]
                        or ancestor::ul[@id="navbar2"] or ancestor::ul[@id="navbar3"]
                        or ancestor::style)]
            /text()[normalize-space()]
            """
        ).getall()

        # Clean up the text content by removing unwanted whitespace characters and extra spaces
        if not text_content:
            return
        cleaned_text_content = " ".join(
            text.strip() for text in text_content if text.strip()
        )

        cleaned_text_content = (
            cleaned_text_content.strip()
            .replace("\n", "")
            .replace("\r", "")
            .replace("\t", "")
            .replace("\u00a0", " ")
        )
        pattern = r"[^a-zA-Z0-9 .,-]"

        # Use re.sub() to replace unwanted characters with an empty string
        cleaned_text = re.sub(pattern, "", cleaned_text_content)
        split_text = cleaned_text.split()
        metadata["word_count"] = len(split_text)
        cleaned_text = " ".join(split_text)

        if len(cleaned_text) == 0:
            return
        # Store the cleaned text content in the dictionary with the URL as the key
        metadata["url"] = response.url
        url_dict["text_content"] = cleaned_text
        url_dict["metadata"] = metadata
        self.scraped_data[response.url] = url_dict
        self.scraped_text += cleaned_text_content

    def closed(self, reason):
        # Save the scraped data into a JSON file
        if len(self.scraped_data) == 0:
            print("no scraped!")
            return
        with open("/app/data/scraped_data_harvard_test.json", "w") as f:
            json.dump(self.scraped_data, f)
        with open("/app/gcp_static_data/scraped_data_harvard_test.json", "w") as f:
            json.dump(self.scraped_data, f)
