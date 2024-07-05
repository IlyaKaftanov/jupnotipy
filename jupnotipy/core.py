import logging
import os
import time
import uuid
import functools

import requests

from .funny_messages import generate_funny_login_message, get_random_notification_text

# init logger
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# global vars
TELEGRAM_BASE_URL = "https://api.telegram.org/bot{bot_token}/"


def get_recent_messages(bot_token, offset=0, limit=20):
    """
    Retrieve recent messages from a Telegram bot.

    :param bot_token: The token for accessing the Telegram bot.
    :type bot_token: str
    :param offset: The offset for fetching messages. Defaults to 0.
    :type offset: int, optional
    :param limit: The maximum number of messages to retrieve. Defaults to 20.
    :type limit: int, optional
    :return: A list of recent messages if successful, None otherwise.
    :rtype: list or None
    """
    params = {"offset": offset, "limit": limit}
    response = requests.get(TELEGRAM_BASE_URL.format(bot_token=bot_token) + "getUpdates", params=params)

    if response.status_code == 200:
        data = response.json()
        if data["ok"]:
            return data["result"]
        else:
            logger.error("request error: %s", data["description"])
            return None
    else:
        logger.error("Failed to retrieve updates error, response code: %s", response.status_code)
        return None


def send_telegram_message(bot_token: str, chat_id: int, message: str):
    """
    Send a message to a Telegram chat.

    :param bot_token: The token for accessing the Telegram bot.
    :type bot_token: str
    :param chat_id: The ID of the chat to send the message to.
    :type chat_id: int
    :param message: The message to send.
    :type message: str
    :return: True if the message was sent successfully, False otherwise.
    :rtype: bool
    """
    send_message_url = TELEGRAM_BASE_URL.format(bot_token=bot_token) + "sendMessage"

    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    response = requests.post(send_message_url, json=payload)

    if response.status_code == 200:
        logger.info("Message sent successfully!")
        return True
    else:
        logger.warning(
            "Failed to send message. Status code: %s with response: %s",
            response.status_code,
            response.text,
        )
        return False


class CredentialsCache:
    """
    A class for managing cached credentials.

    Attributes
    ----------
    credentials_path : str
        The file path for storing credentials.

    Methods
    -------
    exists():
        Check if the credentials file exists.
    save_credentials(credentials: dict):
        Save credentials to the file.
    load_credentials() -> dict:
        Load credentials from the file.
    """

    credentials_path: str = os.path.join(os.path.expanduser("~"), ".jupnotipy")

    @staticmethod
    def exists():
        """
        Check if the credentials file exists.

        :return: True if the credentials file exists, False otherwise.
        :rtype: bool
        """
        return os.path.exists(CredentialsCache.credentials_path)

    @staticmethod
    def save_credentials(credentials: dict):
        """
        Save credentials to the file.

        :param credentials: The credentials to save.
        :type credentials: dict
        :raises ValueError: If 'chat_id' is missing from credentials.
        """
        if "chat_id" not in credentials:
            raise ValueError("missing chat_id")

        # update credentials if not key exists
        # to keep the ability of insert-update like style savings
        if os.path.exists(CredentialsCache.credentials_path):
            prev_credentials = CredentialsCache.load_credentials()
            for key in prev_credentials:
                if key not in credentials:
                    credentials[key] = prev_credentials[key]

        with open(CredentialsCache.credentials_path, "w") as f:
            for key, value in credentials.items():
                f.write(f"{key}={value}\n")

    @staticmethod
    def load_credentials() -> dict:
        """
        Load credentials from the file.

        :return: A dictionary containing the credentials.
        :rtype: dict
        """
        data = {}
        if not os.path.exists(CredentialsCache.credentials_path):
            return data

        with open(CredentialsCache.credentials_path, "r") as f:
            for line in f:
                key, value = line.strip().split("=", 1)
                data[key] = value
        return data


def login(bot_token: str, polling_freq: int = 3, num_retries: int = 10):
    """
    Log in to the Telegram bot by sending a unique message and waiting for a response.

    :param bot_token: The token for accessing the Telegram bot.
    :type bot_token: str
    :param polling_freq: The frequency (in seconds) to poll for messages. Defaults to 3.
    :type polling_freq: int, optional
    :param num_retries: The number of retries for polling. Defaults to 10.
    :type num_retries: int, optional
    """
    awaited_text = str(uuid.uuid4())
    logger.info(
        "Please send a text '%s' to you bot. Time left: %s sec",
        awaited_text,
        polling_freq * num_retries,
    )
    chat_id = 0
    while num_retries:
        recent_messages = get_recent_messages(bot_token)
        if recent_messages:
            for update in recent_messages:
                if "message" in update:
                    message = update["message"]
                    message_text = message.get("text", "")
                    # potentially, you could brute-force the uuid, but it's protected
                    # from telegram side.
                    if awaited_text in message_text:
                        chat_id = message["chat"]["id"]
        if chat_id:
            break
        time.sleep(polling_freq)
        num_retries -= 1
        logger.info(
            "Send message to you bot around %d sec time left.",
            num_retries * polling_freq,
        )

    if chat_id:
        status = send_telegram_message(bot_token, chat_id, generate_funny_login_message())
        if not status:
            logger.info("Failed to send message, please check logs above")
        else:
            CredentialsCache.save_credentials({"chat_id": chat_id, "bot_token": bot_token})
    else:
        logger.error("Failed to obtain chat_id.")


def notify(
    bot_token: str = "",
    chat_id: int = 0,
    message: str = "",
    update_credentials: bool = False,
):
    """
    Send a notification message via the Telegram bot.

    :param bot_token: The token for accessing the Telegram bot. Defaults to an empty string.
    :type bot_token: str, optional
    :param chat_id: The ID of the chat to send the message to. Defaults to 0.
    :type chat_id: int, optional
    :param message: The message to send. Defaults to an empty string.
    :type message: str, optional
    :param update_credentials: Whether to update cached credentials. Defaults to False.
    :type update_credentials: bool, optional
    :raises ValueError: If `bot_token` or `chat_id` is missing.
    """
    credentials = CredentialsCache.load_credentials()
    if not bot_token:
        bot_token = credentials.get("bot_token", "")
    if not chat_id:
        chat_id = credentials.get("chat_id", 0)

    if not bot_token or not chat_id:
        raise ValueError("Login first or check the passed `bot_token` and `chat_id`")

    if not message:
        message = get_random_notification_text()

    status = send_telegram_message(bot_token, chat_id, message)
    if not status:
        logger.info("Failed to send message, please check logs above")
    elif status and update_credentials:
        CredentialsCache.save_credentials({"chat_id": chat_id, "bot_token": bot_token})


def notify_on_end(
    bot_token: str = "",
    chat_id: int = 0,
    message: str = "",
    update_credentials: bool = False,
    max_exception_msg_len: int = 1000,
):
    """
    A decorator to send a notification message when a function ends.

    :param bot_token: The token for accessing the Telegram bot. Defaults to an empty string.
    :type bot_token: str, optional
    :param chat_id: The ID of the chat to send the message to. Defaults to 0.
    :type chat_id: int, optional
    :param message: The message to send. Defaults to an empty string.
    :type message: str, optional
    :param update_credentials: Whether to update cached credentials. Defaults to False.
    :type update_credentials: bool, optional
    :param max_exception_msg_len: The maximum length of the exception message to send. Defaults to 1000.
    :type max_exception_msg_len: int, optional
    :return: The decorated function.
    :rtype: function
    """

    def notify_on_end_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                notify(bot_token, chat_id, message, update_credentials)
                return result
            except Exception as err:
                err_msg = f"error in nested function {err}"
                logger.exception(err_msg, exc_info=True)
                notify(
                    bot_token,
                    chat_id,
                    f"{message} \n finished with error: {err_msg[:max_exception_msg_len]}",
                    update_credentials,
                )

        return wrapper

    return notify_on_end_decorator
