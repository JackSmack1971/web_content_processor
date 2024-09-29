import asyncio
import aiofiles
import os
import random
import hashlib
import logging
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page
import pandas as pd
import gradio as gr
from typing import List, Tuple
from src.config_manager import ConfigManager

class Scraper:
    """Handles web scraping operations."""

    def __init__(self, config: ConfigManager):
        """
        Initialize the Scraper.

        Args:
            config (ConfigManager): Configuration manager instance.
        """
        self.config = config
        self.setup_logging()

    def setup_logging(self):
        """Set up logging for the scraper."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("logs/scraper.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def setup_page(self, playwright):
        """Set up a new browser page for scraping."""
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=self.config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
            viewport={'width': 1920, 'height': 1080},
        )
        page = await context.new_page()
        await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)
        return page, browser

    async def scroll_and_extract(self, page: Page, url: str) -> str:
        """Scroll the page and extract its content."""
        await page.goto(url, wait_until='networkidle')
        
        try:
            await page.click("text='Accept'", timeout=5000)
        except:
            pass

        last_height = await page.evaluate('document.body.scrollHeight')
        
        for _ in range(self.config.get('MAX_SCROLLS', 5)):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(self.config.get('SCROLL_PAUSE_TIME', 2.0) * 1000)
            new_height = await page.evaluate('document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height
        
        await page.wait_for_timeout(5000)
        
        return await page.content()

    def clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract main text."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for element in soup(['nav', 'header', 'footer', 'aside', 'script', 'style']):
            element.decompose()
        
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.body.get_text(separator='\n', strip=True) if soup.body else soup.get_text(separator='\n', strip=True)
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        return text

    def generate_filename(self, url: str) -> str:
        """Generate a filename from the given URL."""
        parsed_url = urlparse(url)
        filename = re.sub(r'[^a-zA-Z0-9_-]', '_', parsed_url.path.strip("/")) or "index"
        if parsed_url.query:
            filename += "_" + hashlib.md5(parsed_url.query.encode()).hexdigest()
        return filename

    async def save_text(self, url: str, text: str) -> None:
        """Save the extracted text to a file."""
        parsed_url = urlparse(url)
        folder_name = parsed_url.netloc.replace("www.", "")
        os.makedirs(os.path.join("data", "output", folder_name), exist_ok=True)
        filename = self.generate_filename(url) + ".txt"
        file_path = os.path.join("data", "output", folder_name, filename)
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(text)
            self.logger.info(f"Saved content for {url} to {file_path}")
        except IOError as e:
            self.logger.error(f"Failed to save content for {url}: {str(e)}")

    async def scrape_url(self, page: Page, url: str) -> bool:
        """Scrape a single URL."""
        try:
            html_content = await self.scroll_and_extract(page, url)
            if html_content:
                cleaned_text = self.clean_html(html_content)
                if "Please turn JavaScript on and reload the page." in cleaned_text:
                    self.logger.warning(f"JavaScript check detected for {url}")
                    return False
                await self.save_text(url, cleaned_text)
                self.logger.info(f"Successfully scraped and saved content for {url}")
                random_delay = random.uniform(self.config.get('DELAY_MIN', 1), self.config.get('DELAY_MAX', 3))
                self.logger.debug(f"Applying random delay of {random_delay:.2f} seconds for {url}")
                await asyncio.sleep(random_delay)
                return True
            else:
                self.logger.warning(f"No content retrieved for {url}")
                return False
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return False

    async def scrape_urls(self, urls: List[str], progress=gr.Progress()) -> Tuple[int, int]:
        """Scrape multiple URLs."""
        async with async_playwright() as playwright:
            page, browser = await self.setup_page(playwright)
            try:
                results = []
                for i, url in enumerate(urls):
                    result = await self.scrape_url(page, url)
                    results.append(result)
                    progress((i + 1) / len(urls), desc=f"Scraping URL {i + 1}/{len(urls)}")
            finally:
                await browser.close()
        
        successes = sum(results)
        failures = len(urls) - successes
        return successes, failures

    def read_urls_from_file(self, file_path: str) -> List[str]:
        """Read URLs from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file if line.strip() and urlparse(line.strip()).scheme]
            self.logger.info(f"Loaded {len(urls)} valid URLs from {file_path}")
            return urls
        except IOError as e:
            self.logger.error(f"Error reading URLs from file: {str(e)}")
            return []

    def run_scraper(self, file_path, progress=gr.Progress()):
        """Run the scraper on URLs from a file."""
        if file_path is None:
            # If no file is uploaded, look for the most recent file in data/input
            input_dir = os.path.join('data', 'input')
            files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
            if not files:
                return pd.DataFrame(), "No input file found. Please upload a file or run link extraction first."
            latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(input_dir, f)))
            file_path = os.path.join(input_dir, latest_file)
        else:
            file_path = file_path.name

        urls = self.read_urls_from_file(file_path)
        if not urls:
            return pd.DataFrame(), "No valid URLs found. Please check your input file."

        self.logger.info(f"Starting the scraping process for {len(urls)} URLs")
        progress(0, desc="Initializing...")

        try:
            successes, failures = asyncio.run(self.scrape_urls(urls, progress))
        except Exception as e:
            self.logger.exception(f"An error occurred during scraping: {str(e)}")
            return pd.DataFrame(), f"An error occurred: {str(e)}"

        results_df = pd.DataFrame({
            "Total URLs": [len(urls)],
            "Successful": [successes],
            "Failed": [failures]
        })

        return results_df, "Scraping completed successfully!"