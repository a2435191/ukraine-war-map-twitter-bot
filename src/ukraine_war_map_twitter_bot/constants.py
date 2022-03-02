# import re
from pathlib import Path

URL = (
    "https://commons.wikimedia.org/wiki/File:Russo-Ukraine_Conflict_(2014-present).svg"
)
DATE_STRING_FORMAT = r"%H:%M, %d %B %Y"

MAX_TWEET_LENGTH = 280
ELLIPSIS = "..."
DESCRIPTION_PREFIX = "New map for the war in #Ukraine"
# EXTRACT_DIMS_FROM_STRING_RE: re.Pattern = re.compile(r'([,\d]+) × ([,\d]+) .+\)$')
MAX_MEDIA_BYTES = 15e6  # 15 MB
TARGET_WIDTH = 2000
BOT_NAME = "Ukraine Mapping Bot"
USER_AGENT = "Ukraine War Mapping Twitter bot (https://github.com/a2435191/ukraine-war-map-twitter-bot)"

LOGS_RELATIVE_PATH = "log.txt"
