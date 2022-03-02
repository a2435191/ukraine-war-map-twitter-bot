from datetime import datetime
from typing import Iterable, NamedTuple

import requests
from bs4 import BeautifulSoup, Tag

from .constants import DATE_STRING_FORMAT, URL
from .logs.log import get_logger, log_fn_enter_and_exit

LOGGER = get_logger(__name__)


class WikimediaPictureData(NamedTuple):
    svg_url: str
    timestamp: int
    description: str
    # dimensions: Tuple[int, int]


@log_fn_enter_and_exit(LOGGER)
def get_latest_ukraine_map() -> WikimediaPictureData:
    """Return the latest uploaded map of Ukraine from Wikimedia Commons.

    Returns:
        WikimediaPictureData: A dataclass representing the picture and some metadata.
    """

    soup = BeautifulSoup(requests.get(URL).text, features="html.parser")
    table = soup.select_one('table[class="wikitable filehistory"]')

    latest_row: Iterable[Tag] = table.find_all("tr")[1].find_all(
        "td"
    )  # 0 is header row
    LOGGER.debug(f"latest_row: {latest_row}")

    # dimensions = tuple([
    #     int(s .replace(',', '').replace(' ', ''))
    #     for s in EXTRACT_DIMS_FROM_STRING_RE.search(latest_row[3].get_text()).group(1, 2)
    # ])

    svg_url = latest_row[1].find("a").get("href")
    timestamp: int = datetime.strptime(
        latest_row[1].find("a").get_text(), DATE_STRING_FORMAT
    ).timestamp()
    description = latest_row[5].text

    return WikimediaPictureData(svg_url, timestamp, description)  # , dimensions)
