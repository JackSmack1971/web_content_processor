import asyncio
import os
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
import pandas as pd
import gradio as gr
from typing import Tuple
from src.config_manager import ConfigManager
import logging

class LinkExtractor:
    """Extracts internal links from a given URL."""

    def __init__(self, config: ConfigManager):
        """
        Initialize the LinkExtractor.

        Args:
            config (ConfigManager): Configuration manager instance.
        """
        self.config = config
        self.setup_logging()

    def setup_logging(self):
        """Set up logging for the link extractor."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                            filename='logs/link_extractor.log')
        self.logger = logging.getLogger(__name__)

    async def setup_page(self, playwright):
        """Set up a new browser page for link extraction."""
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=self.config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
            viewport={'width': 1920, 'height': 1080},
        )
        page = await context.new_page()
        return page, browser

    async def extract_links(self, url: str) -> pd.DataFrame:
        """
        Extract internal links from the given URL.

        Args:
            url (str): The URL to extract links from.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted links.
        """
        async with async_playwright() as playwright:
            page, browser = await self.setup_page(playwright)
            try:
                await page.goto(url, wait_until='networkidle')
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                
                internal_links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    full_url = urljoin(base_url, href)
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        internal_links.append(full_url)
                
                return pd.DataFrame(internal_links, columns=['Internal Links'])
            except Exception as e:
                self.logger.error(f"Error extracting links from {url}: {str(e)}")
                return pd.DataFrame()
            finally:
                await browser.close()

    def run_extractor(self, url: str) -> Tuple[pd.DataFrame, str]:
        """
        Run the link extractor and return results.

        Args:
            url (str): The URL to extract links from.

        Returns:
            Tuple[pd.DataFrame, str]: A tuple containing the DataFrame of links and a status message.
        """
        try:
            df = asyncio.run(self.extract_links(url))
            if df.empty:
                return df, "No internal links found or an error occurred."
            
            # Save the extracted links to a file
            os.makedirs('data/input', exist_ok=True)
            output_file = os.path.join('data/input', f"{urlparse(url).netloc}_links.txt")
            df['Internal Links'].to_csv(output_file, index=False, header=False)
            
            return df, f"Successfully extracted and saved {len(df)} internal links to {output_file}."
        except Exception as e:
            self.logger.error(f"An error occurred while running the extractor: {str(e)}")
            return pd.DataFrame(), f"An error occurred: {str(e)}"