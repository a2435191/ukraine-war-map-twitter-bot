from constants import MAX_TWEET_LENGTH, ELLIPSIS, TARGET_WIDTH, BOT_NAME
from typing import List
from io import BytesIO
import requests
from datetime import datetime
from PIL import Image
from cairosvg import svg2png
from log import get_logger, log_fn_enter_and_exit

LOGGER = get_logger(__name__)

@log_fn_enter_and_exit(LOGGER)
def split_tweet(string: str) -> List[str]:
    if len(string) <= MAX_TWEET_LENGTH:
        LOGGER.debug("string already shorter than MAX_TWEET_LENGTH, so returning [string]")
        return [string]

    out = []
    out.append(string[: MAX_TWEET_LENGTH - len(ELLIPSIS)] + ELLIPSIS)
    string = string[MAX_TWEET_LENGTH - len(ELLIPSIS) :]
    
    LOGGER.debug(f"before loop, out is {out}, string gets cut to {string}")
    while True:
        LOGGER.debug("start of while loop")
        if len(string) <= MAX_TWEET_LENGTH - len(ELLIPSIS):
            LOGGER.debug(f"string (len {len(string)}) is shorter than MAX_TWEET_LENGTH - len(ELLIPSIS)")
            if string != "":
                out.append(ELLIPSIS + string)
                LOGGER.debug(f"string is non empty, so out becomes {out}")
            break
        else:
            substr = string[: MAX_TWEET_LENGTH - 2 * len(ELLIPSIS)]
            out.append(ELLIPSIS + substr + ELLIPSIS)
            string = string[MAX_TWEET_LENGTH - 2 * len(ELLIPSIS) :]
            LOGGER.debug(f"substr: {substr}, out: {out}, string: {string}")

    assert all((len(s) <= MAX_TWEET_LENGTH for s in out)),\
        f"{out} has chunk greater than {MAX_TWEET_LENGTH}"
    
    LOGGER.debug(f"out: {out}")
    return out


@log_fn_enter_and_exit(LOGGER)
def get_png(url: str) -> BytesIO:
    svg = requests.get(url).content

    png_bytes = BytesIO(svg2png(svg))
    png = Image.open(png_bytes)
    LOGGER.debug(f"Converted .svg to .png the first time (size: {len(png_bytes.getvalue())} bytes")
    
    scale_factor = TARGET_WIDTH / png.width
    LOGGER.debug(f"Scale factor: {scale_factor}")
    png_bytes = BytesIO(svg2png(svg, scale=scale_factor))
    
    LOGGER.debug(f"Converted .svg to .png the second time (size: {len(png_bytes.getvalue())} bytes")
    
    return png_bytes

@log_fn_enter_and_exit(LOGGER)
def get_filename(timestamp: int) -> str:
    time_formatted = datetime.fromtimestamp(timestamp)
    return f"{BOT_NAME}_{time_formatted}.png".replace(" ", "_")