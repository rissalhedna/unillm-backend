import os
import re
from urllib.parse import urljoin, urlparse

import scrapy
from scrapy_playwright.page import PageMethod


class StudyInGermanySpider(scrapy.Spider):
    name = "study-in-germany-spider"
    allowed_domains = ["www.study-in-germany.de"]
    start_urls = ["https://www.study-in-germany.de/en/"]

    visited_urls_file = "visited_urls.txt"

    custom_settings = {
        "DEPTH_LIMIT": 99999,
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.114 Safari/537.36"
        ),
        "LOG_LEVEL": "INFO",
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,
        },
        "CONCURRENT_REQUESTS": 16,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 30 * 1000,
        "FEEDS": {
            "output.json": {
                "format": "json",
                "encoding": "utf8",
                "store_empty": False,
                "fields": ["url", "title", "text_content"],
                "indent": 4,
            },
        },
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.visited_urls = set()

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
        scroll_script = """
        async () => {
            let previousHeight = document.body.scrollHeight;
            while (true) {
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(resolve => setTimeout(resolve, 1000));
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

        title = (
            response.css("main h1::text").get()
            or response.css("title::text").get(default="").strip()
        )
        if not title:
            self.logger.warning(f"No title found for URL: {response.url}")

        MAIN_SELECTOR = ".u-module-container"

        text_content = response.css(".u-module-container *::text").getall()

        if not text_content:
            self.logger.warning(
                f"No text found within {MAIN_SELECTOR} for URL: {response.url}"
            )

        cleaned_text = self.clean_text(text_content)

        self.logger.debug(f"Extracted text content: {cleaned_text}")

        if self.contains_personal_info(cleaned_text):
            self.logger.info(
                f"Excluded page containing personal information: {response.url}"
            )
            return

        yield {
            "url": response.url,
            "title": title,
            "text_content": cleaned_text,
        }

        self.mark_url_as_visited(response.url)

        raw_links = response.css('a[href^="/en/"]::attr(href)').getall()
        self.logger.info(f"Found {len(raw_links)} raw links.")

        filtered_links = [
            link
            for link in raw_links
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
        exclusion_term = "Fact Sheet"

        return exclusion_term.lower() in text.lower()

    def clean_text(self, text_list):
        cleaned_text = " ".join([text.strip() for text in text_list if text.strip()])
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        try:
            cleaned_text = bytes(cleaned_text, "utf-8").decode("unicode_escape")
        except UnicodeDecodeError:
            pass

        cleaned_text = cleaned_text.replace('"', '\\"')
        return cleaned_text

    def mark_url_as_visited(self, url: str):
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
