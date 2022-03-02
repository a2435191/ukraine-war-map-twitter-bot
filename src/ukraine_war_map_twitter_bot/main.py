import json
from datetime import datetime
from typing import Any, Callable, Dict, ParamSpec, TypeVar

import tweepy

from .constants import DESCRIPTION_PREFIX, URL
from .logs.log import get_logger, log_fn_enter_and_exit
from .utils import (
    get_filename,
    get_permanent_data,
    get_png,
    split_tweet,
    update_permanent_data,
)
from .wikimedia_download import get_latest_ukraine_map

LOGGER = get_logger(__name__)

class UkraineBot:
    @log_fn_enter_and_exit(LOGGER)
    def __init__(
        self, permanent_data_path: str, twitter_secrets_path: str
    ) -> None:
        self._data_path = permanent_data_path
        self._auth_path = twitter_secrets_path
        self._api = self._auth_and_get_api()

    _ParamTypes = ParamSpec("_ParamTypes")
    _ReturnType = TypeVar("_ReturnType")


    @log_fn_enter_and_exit(LOGGER)
    def _auth_and_get_api(self) -> tweepy.API:
        with open(self._auth_path) as fh:
            secrets: Dict[str, Any] = json.load(fh)
        auth = tweepy.OAuth1UserHandler(**secrets)
        return tweepy.API(auth)

    @log_fn_enter_and_exit(LOGGER)
    def post(self) -> None:
        try:
            latest_data = get_latest_ukraine_map()
            LOGGER.debug(f"latest ukraine map: {latest_data}")

            old_timestamp = get_permanent_data(self._data_path)["latest_timestamp"]

            if latest_data.timestamp <= old_timestamp:
                LOGGER.info(
                    f"latest timestamp ({latest_data.timestamp}) is not "
                    + f"newer than timestamp in {self._auth_path} ({old_timestamp})"
                )
                return

            LOGGER.info(
                f"latest timestamp ({latest_data.timestamp}) is "
                + f"newer than timestamp in {self._data_path} ({old_timestamp})"
            )

            filename = get_filename(latest_data.timestamp)
            LOGGER.debug(f"filename: {filename}")
            file_ = get_png(latest_data.svg_url)

            media: tweepy.Media = self._api.media_upload(filename, file=file_)
            LOGGER.debug(f"media: {media}")

            description_chunks = split_tweet(
                f"Link: {URL}\n\nDescription: " + latest_data.description
            )
            LOGGER.debug(f"description_chunks: {description_chunks}")

            try:
                tweet = self._api.update_status(
                    f"{DESCRIPTION_PREFIX} ({datetime.fromtimestamp(latest_data.timestamp)})",
                    media_ids=[media.media_id],
                )

                LOGGER.debug(
                    f"tweet at https://twitter.com/ua_invasion_bot/status/{tweet.id}"
                )

                target_id: int = tweet.id
                for chunk in description_chunks:
                    LOGGER.info(f"making reply tweet for {chunk}")
                    comment_tweet = self._api.update_status(
                        chunk, in_reply_to_status_id=target_id
                    )
                    target_id = comment_tweet.id
            finally:
                update_permanent_data(self._data_path, {"latest_timestamp": latest_data.timestamp})

        except Exception as e:
            LOGGER.error(e, exc_info=True)
            raise e
