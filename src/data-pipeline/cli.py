import argparse
import subprocess


def scrape_links():
    """Run the Scrapy spider to scrape all links."""
    print("Running scrapy to scrape links...")
    subprocess.run(["scrapy", "runspider", "scrape_links.py"])


def filter_links():
    """Run the Python script to filter links."""
    print("Filtering scraped links...")
    subprocess.run(["python", "filter_links.py"])


def scrape_content():
    """Run the Scrapy spider to scrape content."""
    print("Running scrapy to scrape content...")
    subprocess.run(["scrapy", "runspider", "scrape_content_scrapy.py"])


def main():
    parser = argparse.ArgumentParser(description="CLI for scraping tasks")

    # Add flags for each task
    parser.add_argument(
        "--scrape_links",
        action="store_true",
        help="Scrape all the links under the domain seas.harvard.edu",
    )
    parser.add_argument(
        "--filter_links", action="store_true", help="Filter the scraped links"
    )
    parser.add_argument(
        "--scrape_content", action="store_true", help="Scrape text content with scrapy"
    )

    args = parser.parse_args()

    # Determine which command was run and execute the corresponding function
    if args.scrape_links:
        scrape_links()
    elif args.filter_links:
        filter_links()
    elif args.scrape_content:
        scrape_content()
    else:
        # If no command is provided, print the help message
        parser.print_help()


if __name__ == "__main__":
    main()
