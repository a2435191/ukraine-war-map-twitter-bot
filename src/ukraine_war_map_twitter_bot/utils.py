import json
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List

import requests
from cairosvg import svg2png
from PIL import Image

from .constants import (BOT_NAME, ELLIPSIS, MAX_TWEET_LENGTH,
                        TARGET_WIDTH, USER_AGENT)
from .logs.log import get_logger, log_fn_enter_and_exit

LOGGER = get_logger(__name__)

@log_fn_enter_and_exit(LOGGER)
def split_tweet(string: str) -> List[str]:
    if len(string) <= MAX_TWEET_LENGTH:
        LOGGER.debug(
            "string already shorter than MAX_TWEET_LENGTH, so returning [string]"
        )
        return [string]

    out = []
    out.append(string[: MAX_TWEET_LENGTH - len(ELLIPSIS)] + ELLIPSIS)
    string = string[MAX_TWEET_LENGTH - len(ELLIPSIS) :]

    LOGGER.debug(f"before loop, out is {out}, string gets cut to {string}")
    while True:
        LOGGER.debug("start of while loop")
        if len(string) <= MAX_TWEET_LENGTH - len(ELLIPSIS):
            LOGGER.debug(
                f"string (len {len(string)}) is shorter than MAX_TWEET_LENGTH - len(ELLIPSIS)"
            )
            if string != "":
                out.append(ELLIPSIS + string)
                LOGGER.debug(f"string is non empty, so out becomes {out}")
            break
        else:
            substr = string[: MAX_TWEET_LENGTH - 2 * len(ELLIPSIS)]
            out.append(ELLIPSIS + substr + ELLIPSIS)
            string = string[MAX_TWEET_LENGTH - 2 * len(ELLIPSIS) :]
            LOGGER.debug(f"substr: {substr}, out: {out}, string: {string}")

    assert all(
        (len(s) <= MAX_TWEET_LENGTH for s in out)
    ), f"{out} has chunk greater than {MAX_TWEET_LENGTH}"

    LOGGER.debug(f"out: {out}")
    return out

@log_fn_enter_and_exit(LOGGER)
def get_svg_data(url: str) -> bytes:
    svg_request = requests.get(url, headers={"User-Agent": USER_AGENT})
    svg_request.raise_for_status()
    svg = svg_request.content
    
    return svg

@log_fn_enter_and_exit(LOGGER)
def get_png(svg: str) -> BytesIO:
    png_bytes = BytesIO(svg2png(svg))
    png = Image.open(png_bytes)
    LOGGER.debug(
        f"Converted .svg to .png the first time (size: {len(png_bytes.getvalue())} bytes"
    )

    scale_factor = TARGET_WIDTH / png.width
    LOGGER.debug(f"Scale factor: {scale_factor}")
    png_bytes = BytesIO(svg2png(svg, scale=scale_factor))

    LOGGER.debug(
        f"Converted .svg to .png the second time (size: {len(png_bytes.getvalue())} bytes"
    )

    return png_bytes


@log_fn_enter_and_exit(LOGGER)
def get_filename(timestamp: int) -> str:
    time_formatted = datetime.fromtimestamp(timestamp)
    return f"{BOT_NAME}_{time_formatted}.png".replace(" ", "_")


@log_fn_enter_and_exit(LOGGER)
def get_permanent_data(data_path: str) -> Dict[str, Any]:
    with open(data_path) as fh:
        return json.load(fh)


@log_fn_enter_and_exit(LOGGER)
def update_permanent_data(data_path: str, new: Dict[str, Any]) -> None:
    with open(data_path) as fh:
        old = json.load(fh)
    old.update(new)
    with open(data_path, "w") as fh:
        json.dump(old, fh, indent=2)
