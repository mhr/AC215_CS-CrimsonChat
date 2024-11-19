import scrapy
import json
from urllib.parse import urljoin


class HarvardCrawlerSpider(scrapy.Spider):
    """
    A Scrapy spider for crawling the Harvard SEAS website, collecting links
    by depth level up to a specified depth limit.

    Attributes:
        name (str): The name of the spider.
        allowed_domains (list): The domains allowed for scraping.
        start_urls (list): The initial URLs to start crawling from.
        custom_settings (dict): Custom settings for the spider, including depth limit.
        links_by_depth (dict): A dictionary to store URLs by their depth level.
    """

    name = "harvardcrawler"
    allowed_domains = ["seas.harvard.edu"]
    start_urls = ["https://seas.harvard.edu"]
    custom_settings = {
        "DEPTH_LIMIT": 1,  # 0 is to the deepest, set to 1 for testing
    }

    def __init__(self, *args, **kwargs):
        """
        Initializes the HarvardCrawlerSpider instance, setting up storage
        for URLs by depth level.
        """
        super(HarvardCrawlerSpider, self).__init__(*args, **kwargs)
        # Initialize to store URLs by depth
        self.links_by_depth = {}

    def parse(self, response):
        """
        Parses a response, extracting and storing links at the current depth level,
        then follows internal links.

        Args:
            response (scrapy.http.Response): The HTTP response object from the Scrapy request.

        Yields:
            scrapy.Request: Requests to follow each internal link on the page.
        """
        # Extract all links from the current page
        links = response.css("a::attr(href)").getall()

        # Resolve relative URLs to absolute URLs and filter by domain
        absolute_links = {
            urljoin(response.url, link)
            for link in links
            if "seas.harvard.edu" in urljoin(response.url, link)
        }

        # Current depth
        current_depth = response.meta.get("depth", 0)

        # Initialize the set for this depth if not already
        if current_depth not in self.links_by_depth:
            self.links_by_depth[current_depth] = set()

        # Add the links to the set for the current depth
        self.links_by_depth[current_depth].update(absolute_links)

        # Follow internal links
        for link in absolute_links:
            yield scrapy.Request(url=link, callback=self.parse)

    def closed(self, reason):
        """
        Called when the spider closes. Logs the counts of URLs found at each depth
        and saves them to JSON files in both /app/data and /app/gcp_static_data directories.

        Args:
            reason (str): The reason the spider was closed (e.g., "finished").
        """
        # Log the counts
        for depth, urls in self.links_by_depth.items():
            self.logger.info(f"Depth {depth}: {len(urls)} URLs")

        depth_limit = self.settings.get("DEPTH_LIMIT", 0)

        # Use the correct path inside the container for saving the file
        file_name = f"/app/data/harvard_cs_links_by_depth_{depth_limit}.json"

        # Write the data to the JSON file
        with open(file_name, "w") as f:
            # Convert sets to lists for JSON serialization
            json.dump(
                {depth: list(urls) for depth, urls in self.links_by_depth.items()}, f
            )

        file_name = f"/app/gcp_static_data/harvard_cs_links_by_depth_{depth_limit}.json"

        # Write the data to the JSON file
        with open(file_name, "w") as f:
            # Convert sets to lists for JSON serialization
            json.dump(
                {depth: list(urls) for depth, urls in self.links_by_depth.items()}, f
            )
