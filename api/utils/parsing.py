from bs4 import BeautifulSoup
from dotenv import load_dotenv
from os import getenv
from requests import Session, Response
import logging
from typing import Optional, Dict, Any

load_dotenv()

logger = logging.getLogger(__name__)


class Parsing(Session):
    def __init__(self) -> None:
        super().__init__()
        # Ganti ke domain yang masih aktif
        self.url: str = "https://anichin.cafe"
        self.history_url: Optional[str] = None
        logger.info(f"Initialized Parsing session with URL: {self.url}")

    def __get_html(self, slug: str, **kwargs: Any) -> Optional[str]:
        """Get HTML content from the specified slug."""
        try:
            if slug.startswith("/"):
                url = f"{self.url}{slug}"
            else:
                url = f"{self.url}/{slug}"

            headers: Dict[str, str] = {
                "User-Agent": getenv(
                    "USER_AGENT",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
                "Referer": self.url,
            }

            if kwargs.get("headers"):
                headers.update(kwargs["headers"])
            kwargs["headers"] = headers

            logger.debug(f"Making request to: {url}")
            response: Response = self.get(url, timeout=20, **kwargs)
            response.raise_for_status()

            self.history_url = url
            logger.debug(f"Successfully fetched content from: {url}")
            return response.text

        except Exception as e:
            logger.error(f"Failed to fetch HTML from {slug}: {e}")
            return None

    def get_parsed_html(self, url: str, **kwargs: Any) -> Optional[BeautifulSoup]:
        """Get parsed HTML content using BeautifulSoup."""
        try:
            html_content = self.__get_html(url, **kwargs)
            if html_content:
                parsed = BeautifulSoup(html_content, "html.parser")
                logger.debug(f"Successfully parsed HTML content for: {url}")
                return parsed
            else:
                logger.warning(f"No HTML content to parse for: {url}")
                return None
        except Exception as e:
            logger.error(f"Failed to parse HTML for {url}: {e}")
            return None

    def parsing(self, data: str) -> Optional[BeautifulSoup]:
        """Parse HTML data using BeautifulSoup."""
        try:
            if not data:
                logger.warning("Empty data provided for parsing")
                return None

            parsed = BeautifulSoup(data, "html.parser")
            logger.debug("Successfully parsed provided HTML data")
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse provided data: {e}")
            return None
