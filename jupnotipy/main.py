import logging
import time
import typing as t
import uuid

import requests

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

TELEGRAM_BASE_URL = "https://api.telegram.org/bot{bot_token}/"


def get_recent_messages(bot_token, offset=0, limit=20):
    params = {"offset": offset, "limit": limit}
    response = requests.get(
        TELEGRAM_BASE_URL.format(bot_token=bot_token) + "getUpdates", params=params
    )

    if response.status_code == 200:
        data = response.json()
        if data["ok"]:
            return data["result"]
        else:
            logger.error("request error: %s", data["description"])
            return None
    else:
        logger.error(
            "Failed to retrieve updates error, response code: %s", response.status_code
        )
        return None


def send_telegram_message(bot_token: str, chat_id: int, message: str):
    send_message_url = TELEGRAM_BASE_URL.format(bot_token=bot_token) + "sendMessage"

    payload = {"chat_id": chat_id, "text": message}

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


def generate_text_for_user() -> str:
    return f"{uuid.uuid4()}"


class TNotifier:
    """A class to handle Telegram bot notifications."""

    def __init__(
        self,
        bot_token: str,
        chat_id: t.Optional[int] = None,
        username: t.Optional[str] = None,
    ):
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._username = username

    def _start_polling(
        self, awaited_text: str, polling_freq: int = 3, num_retries: int = 10
    ) -> tuple[t.Optional[int], t.Optional[str]]:
        """
        Start polling for a specific message to initialize the notifier.

        Args:
            awaited_text (str): The text to wait for in incoming messages.
            polling_freq (int, optional): The frequency of polling in seconds. Defaults to 3.
            num_retries (int, optional): The number of polling attempts. Defaults to 10.

        Returns:
            tuple[int | None, str | None]: A tuple containing the chat_id and username if found, (None, None) otherwise.
        """
        logger.info(
            "Please send a text '%s' to you bot. Time left: %s sec",
            awaited_text,
            polling_freq * num_retries,
        )
        while num_retries:
            recent_messages = get_recent_messages(self._bot_token)
            if recent_messages:
                for update in recent_messages:
                    if "message" in update:
                        message = update["message"]
                        message_text = message.get("text", "")
                        # potentially, you could brute-force the uuid, but it's protected
                        # from telegram side.
                        if awaited_text in message_text:
                            chat_id = message["chat"]["id"]
                            username = message["from"]["first_name"]
                            return chat_id, username
            time.sleep(polling_freq)
            num_retries -= 1
        return None, None

    def init_notification(
        self, user_def_text: str = "", polling_freq: int = 3, num_retries: int = 10
    ):
        """
        Initialize the notifier by obtaining the chat_id and username.

        Args:
            user_def_text (str, optional): Custom text to send for initialization. Defaults to "".
            polling_freq (int, optional): Frequency of polling for the initialization message in seconds. Defaults to 3.
        """
        if not user_def_text:
            user_def_text = generate_text_for_user()
        self._chat_id, self._username = self._start_polling(
            user_def_text, polling_freq, num_retries
        )
        status = send_telegram_message(
            self._bot_token, self._chat_id, "successfully initialized notifier"
        )
        if not status:
            logger.info("Failed to send message, please check logs above")

    def get_notification_message(self, text: str = "") -> str:
        """
        Generate the notification message.

        Args:
            text (str, optional): Custom text to include in the message. Defaults to "".

        Returns:
            str: The formatted notification message.
        """
        assert self._username
        if not text:
            text = "😎 work is done, please check the results!"
        return f"{self._username},\n {text}"

    def notify(self, text: str = ""):
        """
        Send a notification message.

        Args:
            text (str, optional): The text to send. Defaults to "".

        Raises:
            AssertionError: If init_notification method hasn't been called.
        """
        assert self._chat_id and self._username, (
            f"call `init_notification` method first \n"
            f"or chat_id({self._chat_id}) and username({self._username}) predefined incorrectly"
        )
        status = send_telegram_message(
            self._bot_token, self._chat_id, self.get_notification_message(text)
        )
        if not status:
            logger.error("Failed to send message, please check logs above")
