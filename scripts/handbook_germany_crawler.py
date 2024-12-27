import os  # Added to handle file operations
import re
from urllib.parse import urljoin, urlparse

import scrapy
from scrapy_playwright.page import PageMethod


class HandbookGermanySpider(scrapy.Spider):
    name = "handbook-germany-spider"
    allowed_domains = ["handbookgermany.de"]
    start_urls = ["https://handbookgermany.de/en"]

    # Path to the file storing visited URLs
    visited_urls_file = "visited_urls.txt"

    custom_settings = {
        "DEPTH_LIMIT": 2,
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.114 Safari/537.36"
        ),
        "LOG_LEVEL": "INFO",  # Adjust as needed
        # Playwright settings
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,  # Set to False if you want to see the browser actions
            # Add more Playwright launch options if needed
        },
        "CONCURRENT_REQUESTS": 16,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 30 * 1000,  # 30 seconds
        # Feed export settings
        "FEEDS": {
            "output.json": {
                "format": "json",
                "encoding": "utf8",
                "store_empty": False,
                "fields": ["url", "title", "text_content"],
                "indent": 4,
            },
        },
        # Fix for ScrapyDeprecationWarning
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize the set of visited URLs
        self.visited_urls = set()

        # Load visited URLs from the file if it exists
        if os.path.exists(self.visited_urls_file):
            with open(self.visited_urls_file, "r", encoding="utf-8") as f:
                for line in f:
                    url = line.strip()
                    if url:
                        self.visited_urls.add(url)
            self.logger.info(
                f"Loaded {len(self.visited_urls)} visited URLs from {self.visited_urls_file}"
            )
        else:
            # Create the file if it doesn't exist
            open(self.visited_urls_file, "a").close()
            self.logger.info(
                f"Created new visited URLs file at {self.visited_urls_file}"
            )

    def start_requests(self):
        for url in self.start_urls:
            if url not in self.visited_urls:
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": self.get_playwright_page_methods(),
                    },
                )
            else:
                self.logger.info(f"Skipping already visited URL: {url}")

    def get_playwright_page_methods(self):
        """
        Define a sequence of PageMethods to perform dynamic scrolling until the end of the page.
        """
        scroll_script = """
        async () => {
            let previousHeight = document.body.scrollHeight;
            while (true) {
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for 1 second
                let newHeight = document.body.scrollHeight;
                if (newHeight === previousHeight){
                    break;
                }
                previousHeight = newHeight;
            }
        }
        """
        return [PageMethod("evaluate", scroll_script)]

    def parse(self, response, **kwargs):
        self.logger.info(f"Parsing URL: {response.url}")

        # Extract the title
        title = (
            response.css(".page-title *::text").get()
            or response.css("title::text").get(default="").strip()
        )

        if not title:
            self.logger.warning(f"No title found for URL: {response.url}")

        # Define the main container selector
        MAIN_SELECTOR = ".layout-container"

        # Extract all text within .u-module-container
        # This includes text from all descendant elements
        text_content = response.css(".layout-container *::text").getall()

        if not text_content:
            self.logger.warning(
                f"No text found within {MAIN_SELECTOR} for URL: {response.url}"
            )

        # Clean and join the extracted text
        cleaned_text = self.clean_text(text_content)

        self.logger.debug(f"Extracted text content: {cleaned_text}")

        # Exclude pages containing personal information based on content
        if self.contains_personal_info(cleaned_text):
            self.logger.info(
                f"Excluded page containing personal information: {response.url}"
            )
            return  # Skip processing and yielding data

        # Yield the extracted data
        yield {
            "url": response.url,
            "title": title,
            "text_content": cleaned_text,
        }

        # Add the URL to the visited set and file
        self.mark_url_as_visited(response.url)

        # Extract and filter links
        raw_links = response.css('a[href^="/en/"]::attr(href)').getall()
        self.logger.info(f"Found {len(raw_links)} raw links.")

        filtered_links = [
            link
            for link in raw_links  # type: ignore
            if not re.match(
                r"^/en/(data-privacy-statement|netiquette|get-in-touch|imprint|tag-search|search|plan-your-studies/study-options/programme/higher-education-compass)/",
                link,
            )
        ]

        for i, link in enumerate(filtered_links):
            filtered_links[i] = link.replace("/de/", "/en/")

        self.logger.info(
            f"Filtered down to {len(filtered_links)} links after exclusions."
        )

        # Follow the filtered links using Playwright
        for link in filtered_links:
            absolute_url = urljoin(response.url, link)
            parsed_url = urlparse(absolute_url)
            domain = parsed_url.netloc

            if domain.lower() in self.allowed_domains:
                if absolute_url not in self.visited_urls:
                    yield scrapy.Request(
                        absolute_url,
                        callback=self.parse,
                        meta={
                            "playwright": True,
                            "playwright_page_methods": self.get_playwright_page_methods(),
                        },
                    )
                else:
                    self.logger.info(f"Skipping already visited URL: {absolute_url}")
            else:
                self.logger.debug(
                    f"Excluded URL due to domain mismatch: {absolute_url}"
                )

    def contains_personal_info(self, text: str) -> bool:
        """
        Checks if the provided text contains personal information based on the presence of "Our Bloggers".
        """
        # Define the specific term to look for
        exclusion_term = "Fact Sheet"

        # Perform a case-insensitive search for the term
        return exclusion_term.lower() in text.lower()

    def clean_text(self, text_list):
        """
        Cleans and joins a list of text strings.
        - Converts HTML entities.
        - Strips and normalizes whitespace.
        - Escapes double quotes to prevent JSON interference.
        """
        # Join the text and remove unwanted patterns
        cleaned_text = " ".join([text.strip() for text in text_list if text.strip()])
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        # Replace unicode escape sequences with actual characters
        try:
            cleaned_text = bytes(cleaned_text, "utf-8").decode("unicode_escape")
        except UnicodeDecodeError:
            # If decoding fails, keep the original text
            pass

        # Escape double quotes to prevent JSON interference
        cleaned_text = cleaned_text.replace('"', '\\"')
        return cleaned_text

    def mark_url_as_visited(self, url: str):
        """
        Marks a URL as visited by adding it to the visited_urls set and appending it to the file.
        """
        if url not in self.visited_urls:
            self.visited_urls.add(url)
            try:
                with open(self.visited_urls_file, "a", encoding="utf-8") as f:
                    f.write(f"{url}\n")
                self.logger.debug(f"Marked URL as visited: {url}")
            except Exception as e:
                self.logger.error(f"Failed to mark URL as visited: {url}. Error: {e}")

    def closed(self, reason):
        self.logger.info(f"Spider closed: {reason}")
