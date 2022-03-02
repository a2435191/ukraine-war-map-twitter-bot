from constants import DESCRIPTION_PREFIX, URL, AUTH_PATH, DATA_PATH
import tweepy
from datetime import datetime
from wikimedia_download import get_latest_ukraine_map
from utils import (
    split_tweet,
    get_filename,
    get_png,
    get_permanent_data,
    update_permanent_data,
)
from typing import Dict, Any
import json
from log import get_logger, log_fn_enter_and_exit

LOGGER = get_logger(__name__)


@log_fn_enter_and_exit(LOGGER)
def auth_and_get_api() -> tweepy.API:
    with open(AUTH_PATH) as fh:
        secrets: Dict[str, Any] = json.load(fh)
    auth = tweepy.OAuth1UserHandler(**secrets)
    return tweepy.API(auth)


API = auth_and_get_api()


@log_fn_enter_and_exit(LOGGER)
def post() -> None:
    latest_data = get_latest_ukraine_map()
    LOGGER.debug(f"latest ukraine map: {latest_data}")

    old_timestamp = get_permanent_data()["latest_timestamp"]

    if latest_data.timestamp <= old_timestamp:
        LOGGER.info(
            f"latest timestamp ({latest_data.timestamp}) is not "
            + f"newer than timestamp in {DATA_PATH} ({old_timestamp})"
        )
        return

    LOGGER.info(
        f"latest timestamp ({latest_data.timestamp}) is "
        + f"newer than timestamp in {DATA_PATH} ({old_timestamp})"
    )

    filename = get_filename(latest_data.timestamp)
    LOGGER.debug(f"filename: {filename}")
    file_ = get_png(latest_data.svg_url)

    media: tweepy.Media = API.media_upload(filename, file=file_)
    LOGGER.debug(f"media: {media}")

    description_chunks = split_tweet(
        f"Link: {URL}\n\nDescription: " + latest_data.description
    )
    LOGGER.debug(f"description_chunks: {description_chunks}")

    try:
        tweet = API.update_status(
            f"{DESCRIPTION_PREFIX} ({datetime.fromtimestamp(latest_data.timestamp)})",
            media_ids=[media.media_id],
        )

        LOGGER.debug(f"tweet at https://twitter.com/ua_invasion_bot/status/{tweet.id}")
        
        target_id: int = tweet.id
        for chunk in description_chunks:
            LOGGER.info(f"making reply tweet for {chunk}")
            comment_tweet = API.update_status(chunk, in_reply_to_status_id=target_id)
            target_id = comment_tweet.id
    finally:
        update_permanent_data({"latest_timestamp": latest_data.timestamp})


if __name__ == "__main__":
    try:
        post()
    except Exception as e:
        LOGGER.error(e, exc_info=True)
