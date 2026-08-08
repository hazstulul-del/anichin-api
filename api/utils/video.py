from .parsing import Parsing
from urllib.parse import urlparse
import logging
from typing import Dict, List, Optional, Any, Union
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Video(Parsing):
    def __init__(self, slug: str) -> None:
        super().__init__()
        self.slug: str = slug
        logger.info(f"Initialized Video scraper for slug: {slug}")

    def get_details(self) -> Union[Dict[str, Any], bool]:
        """Get video details for the specified slug."""
        try:
            logger.info(f"Starting to fetch video details for slug: {self.slug}")

            data = self.get_parsed_html(self.slug)
            if not data:
                logger.error("Failed to get video page data")
                return False

            return self.__get_video(data)

        except Exception as e:
            logger.error(f"Error in get_details for slug {self.slug}: {e}")
            return False

    def __get_video(self, data: BeautifulSoup) -> Union[Dict[str, Any], bool]:
        """Extract video sources from the page."""
        try:
            servers = []

            # 1. Cari semua iframe (paling umum)
            iframes = data.find_all("iframe")
            for iframe in iframes:
                src = iframe.get("src") or iframe.get("data-src")
                if src and ("http" in src or src.startswith("//")):
                    if src.startswith("//"):
                        src = "https:" + src

                    # Skip iklan / tracking
                    if any(x in src.lower() for x in ["ads", "doubleclick", "googlesyndication"]):
                        continue

                    servers.append({
                        "name": self.__guess_server_name(src),
                        "url": src,
                        "quality": "default"
                    })

            # 2. Cari select mirror (kalau masih ada)
            video_select = data.find("select", class_="mirror") or data.find("select", {"id": "mirror"})
            if video_select:
                for option in video_select.find_all("option"):
                    value = option.get("value")
                    text = option.text.strip()
                    if value and text and value.startswith("http"):
                        servers.append({
                            "name": text or "Mirror",
                            "url": value,
                            "quality": "default"
                        })

            # 3. Cari data-src / embed di div player
            player_divs = data.find_all(["div", "video"], class_=lambda x: x and ("player" in x.lower() or "embed" in x.lower() or "video" in x.lower()))
            for div in player_divs:
                src = div.get("data-src") or div.get("data-url")
                if src and "http" in src:
                    servers.append({
                        "name": "Player",
                        "url": src,
                        "quality": "default"
                    })

            # Hapus duplikat
            unique_servers = []
            seen = set()
            for s in servers:
                if s["url"] not in seen:
                    seen.add(s["url"])
                    unique_servers.append(s)

            if not unique_servers:
                logger.warning("No video sources found")
                return False

            result = {
                "slug": self.slug,
                "title": self.slug.replace("-", " ").title(),
                "servers": unique_servers,
                "url": unique_servers[0]["url"] if unique_servers else None
            }

            logger.info(f"Found {len(unique_servers)} video sources")
            return result

        except Exception as e:
            logger.error(f"Error extracting video data: {e}")
            return False

    def __guess_server_name(self, url: str) -> str:
        """Tebak nama server dari URL."""
        url_lower = url.lower()
        if "ok.ru" in url_lower or "odnoklassniki" in url_lower:
            return "OK.ru"
        if "dood" in url_lower:
            return "Doodstream"
        if "streamtape" in url_lower:
            return "Streamtape"
        if "mp4upload" in url_lower:
            return "Mp4Upload"
        if "fembed" in url_lower or "femax" in url_lower:
            return "Fembed"
        if "youtube" in url_lower:
            return "YouTube"
        if "vidstream" in url_lower:
            return "Vidstream"
        return "Server"
